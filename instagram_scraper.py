from typing import Dict, List
from datetime import datetime
import instaloader
import json
import time
def get_post_info(post) -> Dict:
    """Extract available information from a post"""
    try:
        info = {
            'shortcode': post.shortcode,
            'url': f'https://www.instagram.com/p/{post.shortcode}/',
            'is_video': False,
            'type': 'Photo'
        }
        
        # Try to get additional information safely
        try:
            info['date'] = post.date_local.strftime('%Y-%m-%d %H:%M:%S')
        except:
            info['date'] = 'Unknown'
            
        try:
            info['caption'] = post.caption if post.caption else 'No caption'
        except:
            info['caption'] = 'No caption'
            
        try:
            info['is_video'] = bool(post.is_video)
            info['type'] = 'Reel' if post.is_video else 'Photo'
        except:
            pass
            
        return info
    except Exception as e:
        return {
            'error': f'Could not fetch post info: {str(e)}',
            'url': f'https://www.instagram.com/p/{post.shortcode}' if hasattr(post, 'shortcode') else 'Unknown'
        }

def scrape_profile(username: str, max_posts: int = 10) -> Dict:
    """
    Scrape basic public information and recent posts from an Instagram profile without login
    
    Args:
        username: Instagram username to scrape
        max_posts: Maximum number of recent posts to fetch (default: 10)
    """
    # Create an instance of Instaloader with reduced request rate
    L = instaloader.Instaloader(
        download_pictures=False,   # Don't download photos
        download_videos=False,     # Don't download videos
        download_video_thumbnails=False,
        download_geotags=False,
        download_comments=False,
        save_metadata=False,
        compress_json=False
    )
    
    # Add delay between requests to avoid rate limiting
    L.context.sleep = lambda *args, **kwargs: time.sleep(2)
    
    try:
        # Get profile information
        profile = instaloader.Profile.from_username(L.context, username)
        
        # Collect basic profile information
        profile_info = {
            'username': profile.username,
            'full_name': profile.full_name if profile.full_name else username,
            'biography': profile.biography if profile.biography else '',
            'posts_count': profile.mediacount,
            'is_private': profile.is_private,
            'external_url': profile.external_url if profile.external_url else '',
            'scraped_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        # Try to get follower and following counts
        try:
            profile_info['followers'] = profile.followers
            profile_info['following'] = profile.followees
        except Exception as e:
            profile_info['followers'] = 'Not available'
            profile_info['following'] = 'Not available'
        
        # Try to get recent posts if profile is public
        if not profile.is_private:
            posts = []
            try:
                # Get post iterator with minimal information
                post_iterator = profile.get_posts()
                
                print(f"\nFetching up to {max_posts} recent posts...")
                for idx, post in enumerate(post_iterator, 1):
                    if len(posts) >= max_posts:
                        break
                        
                    print(f"Fetching post {idx}/{max_posts}...")
                    post_info = get_post_info(post)
                    
                    if 'error' not in post_info:
                        posts.append(post_info)
                    
                    # Add extra delay every 5 posts
                    if idx % 5 == 0:
                        time.sleep(2)
                        
                profile_info['recent_posts'] = posts
                profile_info['posts_fetched'] = len(posts)
                
            except instaloader.exceptions.LoginRequiredException:
                profile_info['recent_posts'] = []
                profile_info['posts_fetched'] = 0
                profile_info['posts_error'] = 'Login required to view posts'
                
            except Exception as e:
                profile_info['recent_posts'] = []
                profile_info['posts_fetched'] = 0
                profile_info['posts_error'] = f'Error fetching posts: {str(e)}'
        else:
            profile_info['recent_posts'] = []
            profile_info['posts_fetched'] = 0
            profile_info['posts_error'] = 'Profile is private'
        
        return profile_info
    
    except instaloader.exceptions.ProfileNotExistsException:
        return {'error': f'Profile {username} does not exist'}
    except instaloader.exceptions.LoginRequiredException:
        return {'error': 'This profile requires login to view'}
    except instaloader.exceptions.ConnectionException:
        return {'error': 'Connection error. Instagram might be rate-limiting requests'}
    except Exception as e:
        return {'error': f'An error occurred: {str(e)}'}

if __name__ == "__main__":
    # Get username and post count from user input
    username = input("Enter Instagram username to scrape: ").strip()
    max_posts = input("Enter number of recent posts to fetch (default 10): ").strip()
    
    if not username:
        print("Error: Username cannot be empty")
    else:
        try:
            max_posts = int(max_posts) if max_posts else 10
        except ValueError:
            print("Invalid number, using default of 10 posts")
            max_posts = 10
            
        print(f"\nScraping public profile information and up to {max_posts} recent posts for @{username}...")
        print("(Note: This may take a while due to rate limiting)")
        
        profile_data = scrape_profile(username, max_posts)
        
        # Check for errors
        if 'error' in profile_data:
            print(f"\nError: {profile_data['error']}")
        else:
            # Print profile information
            print("\nProfile Information:")
            for key, value in profile_data.items():
                if key != 'recent_posts':
                    print(f"{key}: {value}")
            
            # Print posts information
            if profile_data.get('recent_posts'):
                print(f"\nRecent Posts (showing {len(profile_data['recent_posts'])} posts):")
                for i, post in enumerate(profile_data['recent_posts'], 1):
                    print(f"\nPost {i}:")
                    print(json.dumps(post, indent=2))
