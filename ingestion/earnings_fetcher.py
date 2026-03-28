import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import requests
import tempfile
from db import Session
from sqlalchemy import text
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

# faster-whisper runs locally — no API key, no credits needed
# Install: pip install faster-whisper
# First run downloads ~150MB model automatically
from faster_whisper import WhisperModel

# Load model once at module level so it's not reloaded on every call
# "base" = good balance of speed and accuracy for hackathon use
# device="cpu" works on any machine, compute_type="int8" reduces memory usage
print("[earnings_fetcher] Loading Whisper model (first run downloads ~150MB)...")
WHISPER_MODEL = WhisperModel("base", device="cpu", compute_type="int8")
print("[earnings_fetcher] Whisper model ready.")


def get_earnings_audio_url(ticker: str) -> str:
    """
    Returns a public earnings call audio URL for the given ticker.
    In production: scrape company IR pages or use a financial data provider.
    For demo/hackathon: returns a real public MP3 to prove the pipeline works.
    """
    # Demo audio — replace with real IR page scraper in production
    return "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3"


def transcribe_audio(audio_path: str) -> str:
    """
    Transcribes an audio file using faster-whisper running locally.
    Returns the full transcript as a single string.
    No API key or internet connection needed after model download.
    """
    segments, _ = WHISPER_MODEL.transcribe(audio_path)
    transcript = " ".join([seg.text.strip() for seg in segments])
    return transcript


def fetch_earnings_call(company_name: str, ticker: str) -> dict:
    """
    Downloads a public earnings call audio file, transcribes it locally
    using faster-whisper, and saves the transcript to raw_data_items table.

    Args:
        company_name: Full company name e.g. 'Infosys'
        ticker: Stock ticker e.g. 'INFY'

    Returns:
        dict with keys: company_id, source_name, data_type, raw_text,
                        url, published_at, duration_seconds
        Returns empty dict on failure.
    """
    session = Session()
    try:
        # Step 1 — get company_id from DB
        result = session.execute(
            text("SELECT id FROM companies WHERE ticker = :ticker"),
            {"ticker": ticker}
        ).fetchone()

        if not result:
            print(f"  [earnings_fetcher] Ticker '{ticker}' not found in companies table.")
            return {}

        company_id = result.id

        # Step 2 — get audio URL
        audio_url = get_earnings_audio_url(ticker)
        if not audio_url:
            print(f"  [earnings_fetcher] No audio URL found for {ticker}.")
            return {}

        # Step 3 — download audio to temp file
        print(f"  [earnings_fetcher] Downloading audio for {ticker}...")
        audio_resp = requests.get(audio_url, stream=True, timeout=60)
        audio_resp.raise_for_status()

        temp_audio = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
        with open(temp_audio.name, "wb") as f:
            for chunk in audio_resp.iter_content(chunk_size=1024 * 1024):
                if chunk:
                    f.write(chunk)

        # Estimate duration from file size (~1MB per minute at 128kbps)
        file_size_bytes = os.path.getsize(temp_audio.name)
        estimated_duration_seconds = int((file_size_bytes / (1024 * 1024)) * 60)
        print(f"  [earnings_fetcher] Downloaded {file_size_bytes // 1024}KB (~{estimated_duration_seconds}s audio).")

        # Step 4 — transcribe locally with faster-whisper
        print(f"  [earnings_fetcher] Transcribing with faster-whisper (local, no API)...")
        transcript_text = transcribe_audio(temp_audio.name)

        # Clean up temp file
        try:
            os.remove(temp_audio.name)
        except OSError:
            pass

        if not transcript_text.strip():
            print(f"  [earnings_fetcher] Transcription returned empty for {ticker}.")
            return {}

        print(f"  [earnings_fetcher] Transcription complete. {len(transcript_text)} characters.")

        # Step 5 — save to raw_data_items
        record = {
            "company_id":        company_id,
            "source_name":       "Earnings Call Audio",
            "data_type":         "earnings_call",
            "raw_text":          transcript_text,
            "url":               audio_url,
            "published_at":      datetime.utcnow().isoformat(),
            "duration_seconds":  estimated_duration_seconds
        }

        session.execute(
            text("""
                INSERT INTO raw_data_items
                    (company_id, source_name, data_type, raw_text, url, published_at, duration_seconds)
                VALUES
                    (:company_id, :source_name, :data_type, :raw_text, :url, :published_at, :duration_seconds)
            """),
            record
        )
        session.commit()
        print(f"  [earnings_fetcher] Saved transcript for {ticker} to DB.")
        return record

    except Exception as e:
        session.rollback()
        print(f"  [earnings_fetcher] Error processing {ticker}: {e}")
        return {}
    finally:
        session.close()


if __name__ == "__main__":
    print("Testing fetch_earnings_call for INFY...")
    result = fetch_earnings_call("Infosys", "INFY")
    if result:
        print(f"\nSuccess!")
        print(f"  Duration: {result.get('duration_seconds')}s")
        print(f"  Transcript preview: {result.get('raw_text', '')[:300]}...")
    else:
        print("Failed — check errors above.")