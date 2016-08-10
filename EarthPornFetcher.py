# EarthPornFetcher - Tool to fetch new images from /r/EarthPorn to be used as Wallpapers
import os, re, praw, urllib, imghdr, glob, httplib
from PIL import Image, ImageChops, ImageOps
from urlparse import urlparse

LIMIT = 2500
REQUIRED_WIDTH = 5120
REQUIRED_HEIGHT = 1440 
RES_REGEXP = re.compile('(\d+)\s*[x|X]*\s*(\d+)')
DOWNLOAD_LOCATION = os.path.join('F:', os.sep, 'Wallpapers', 'Slideshow', 'EarthPornFetcher')

def main():
  r = praw.Reddit(user_agent='EarthPornFetcher')
  submissions = r.get_subreddit('EarthPorn').get_hot(limit=LIMIT)
  
  # Create download location if it does not exist
  if not os.path.exists(DOWNLOAD_LOCATION):
    os.makedirs(DOWNLOAD_LOCATION)
  
  # Iterate through images
  for entry in submissions:
    # Skip stickied posts
    if entry.stickied:
      continue
    
    # Skip self posts
    if entry.is_self:
      continue;
      
    # Check resolution based on title naming convention
    title = entry.title.encode("utf-8")
    
    res = RES_REGEXP.search(title)
    width, height = int(res.group(1)), int(res.group(2))

    # Check if image is large enough
    if width < REQUIRED_WIDTH or height < REQUIRED_HEIGHT:
      continue;
      
    reddit_unique_id =  entry.id
    
    # Skip if file exists
    target_file = DOWNLOAD_LOCATION + os.sep + reddit_unique_id
    if glob.glob(target_file + '*'):
      continue
    
    # Process image
    imageurl = entry.url
    
    if "imgur.com" in imageurl and "i.imgur.com" not in imageurl:
      imageurl = imageurl.replace('imgur.com', 'i.imgur.com') + ".jpg" #replace imgur link
    
    # Don't process non successful requests
    imageurl_parsed = urlparse(imageurl)
    print imageurl_parsed.netloc, imageurl_parsed.path
    
    status = get_status_code(imageurl_parsed.netloc, imageurl_parsed.path)
    if (not status or status != 200):
      continue
    
    # Download image
    try:
      urllib.urlretrieve(imageurl,  target_file)
    except Exception,e:
      continue
    
    file_type = imghdr.what(target_file)
    
    # Skip if file is not a proper image
    if not file_type:
      os.remove(target_file)
      continue
    
    target_file_with_type = target_file + '.' + file_type
    os.rename(target_file, target_file_with_type)
    
    # Resize image
    makeThumb(target_file_with_type, target_file_with_type, pad=False)

# Source: https://stackoverflow.com/a/9103783/1800854
def makeThumb(f_in, f_out, size=(REQUIRED_WIDTH, REQUIRED_HEIGHT), pad=False):

    image = Image.open(f_in)
    image.thumbnail(size, Image.ANTIALIAS)
    image_size = image.size

    if pad:
        thumb = image.crop( (0, 0, size[0], size[1]) )

        offset_x = max( (size[0] - image_size[0]) / 2, 0 )
        offset_y = max( (size[1] - image_size[1]) / 2, 0 )

        thumb = ImageChops.offset(thumb, offset_x, offset_y)

    else:
        thumb = ImageOps.fit(image, size, Image.ANTIALIAS, (0.5, 0.5))

    thumb.save(f_out)
    

# Source: https://stackoverflow.com/a/1140822/1800854
def get_status_code(host, path="/"):
  """ This function retreives the status code of a website by requesting
      HEAD data from the host. This means that it only requests the headers.
      If the host cannot be reached or something else goes wrong, it returns
      None instead.
  """
  try:
      conn = httplib.HTTPConnection(host)
      conn.request("HEAD", path)
      return conn.getresponse().status
  except StandardError:
      return None
        
if __name__ == "__main__":
  main()