import yt_dlp
from pydantic import BaseModel, ValidationError
from typing import Optional
import json

class MetaData(BaseModel):
    id: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    _type: Optional[str] = None
    entries: Optional[list] = None
    webpage_url: Optional[str] = None
    original_url: Optional[str] = None
    webpage_url_basename: Optional[str] = None
    webpage_url_domain: Optional[str] = None
    extractor: Optional[str] = None
    extractor_key: Optional[str] = None
    release_year: Optional[int] = None
    playlist_count: Optional[int] = None
    epoch: Optional[int] = None


def meta_data_info(url):
    ydl_opts = {
        'extract_flat': True,
        'quiet': True,
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            validated_data = MetaData(**info).model_dump()
    
        # Save to JSON file
        with open('metadata.json', 'w', encoding='utf-8') as f:
            json.dump(validated_data, f, indent=4, ensure_ascii=False)
        
        return validated_data
        
    except ValidationError as e:
        print(f"Validation error: {e}")
        return None
    except Exception as e:
        print(f"Error extracting metadata: {e}")
        return None

if __name__ == "__main__":
    print(meta_data_info("https://www.instagram.com/p/DFRIscGtYa6/"))

