# Part A: The Imports library
import asyncio # running asynchronous operations
import httpx # The library for making HTTP requests
import os # for interacting with OS (Manipulate files & Folders.)
import argparse # For parsing command-line arguments
import time # For timing the downloads

# Part B: Downloading a Single File

async def download_file(client, url):
    """Download a single file from URL"""
    try:
        print(f"Starting download: {url}")
        
        # Extract filename from URL
        filename = url.split('/')[-1] # -1 gets the last part after splitting by '/'
        if not filename or '.' not in filename:
            filename = f"file_{int(time.time())}.jpg"  # Default filename with timestamp
        
        # Create downloads directory if it doesn't exist
        os.makedirs('downloads', exist_ok=True)
        
        # Create the full path where to save the file
        filepath = os.path.join('downloads', filename)
        
        # Make the HTTP request
        response = await client.get(url)
        response.raise_for_status()  # Raise an error for bad status codes
        
        # Write the file to disk
        with open(filepath, 'wb') as file:
            async for chunk in response.aiter_bytes():
                file.write(chunk)
        
        print(f"✓ Downloaded: {filename}")
        return filepath
        
    except Exception as e:
        print(f"✗ Failed to download {url}: {str(e)}")
        return None

# Part C: Downloading Multiple Files Concurrently

async def download_multiple_files(urls, max_concurrent=5):
    """Download multiple files concurrently with a limit on concurrent downloads"""
    semaphore = asyncio.Semaphore(max_concurrent)
    
    async def download_with_semaphore(client, url):
        async with semaphore:
            return await download_file(client, url)
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        tasks = [download_with_semaphore(client, url) for url in urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
    return results

# Part D: Reading URLs from File

def read_urls_from_file(filepath):
    """Read URLs from a text file, one URL per line"""
    try:
        with open(filepath, 'r') as file:
            urls = [line.strip() for line in file if line.strip()]
        return urls
    except FileNotFoundError:
        print(f"Error: File {filepath} not found")
        return []
    except Exception as e:
        print(f"Error reading file {filepath}: {str(e)}")
        return []

# Part E: Main Function and CLI

async def main():
    """Main function to handle command-line arguments and start downloads"""
    parser = argparse.ArgumentParser(description='Download assets from URLs')
    parser.add_argument('--file', '-f', default='urls.txt', 
                       help='File containing URLs to download (default: urls.txt)')
    parser.add_argument('--concurrent', '-c', type=int, default=5,
                       help='Maximum concurrent downloads (default: 5)')
    parser.add_argument('--url', '-u', 
                       help='Download a single URL')
    
    args = parser.parse_args()
    
    start_time = time.time()
    
    if args.url:
        # Download single URL
        async with httpx.AsyncClient(timeout=30.0) as client:
            result = await download_file(client, args.url)
            if result:
                print(f"File saved to: {result}")
    else:
        # Download multiple URLs from file
        urls = read_urls_from_file(args.file)
        if not urls:
            print("No URLs found to download")
            return
        
        print(f"Found {len(urls)} URLs to download")
        print(f"Max concurrent downloads: {args.concurrent}")
        print("-" * 50)
        
        results = await download_multiple_files(urls, args.concurrent)
        
        # Count successful downloads
        successful = sum(1 for result in results if result is not None and not isinstance(result, Exception))
        failed = len(results) - successful
        
        print("-" * 50)
        print(f"Download complete!")
        print(f"Successful: {successful}")
        print(f"Failed: {failed}")
        print(f"Total time: {time.time() - start_time:.2f} seconds")

if __name__ == "__main__":
    asyncio.run(main())
