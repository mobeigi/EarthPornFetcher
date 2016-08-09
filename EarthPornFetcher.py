# EarthPornFetcher - Tool to fetch new images from /r/EarthPorn to be used as Wallpapers
import os, re, praw, urllib, imghdr, glob
from PIL import Image, ImageChops, ImageOps

LIMIT = 1000
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
    
    # Download image
    imageurl = entry.url
    
    if "i.imgur.com" not in imageurl: 
      imageurl = imageurl.replace('imgur.com', 'i.imgur.com') + ".jpg" #replace imgur link
    
    urllib.urlretrieve(imageurl,  target_file)
    file_type = imghdr.what(target_file)
    
    # Skip if file is not a proper image
    if not file_type:
      os.remove(target_file)
      continue
    
    target_file_with_type = target_file + '.' + file_type
    os.rename(target_file, target_file_with_type)
    
    # Resize image
    #new_width  = REQUIRED_WIDTH
    #new_height = new_width * height / width
    
    #new_width  = REQUIRED_WIDTH
    #new_height = new_width * height / width
    
    #img = Image.open(target_file_with_type)
    #img = img.resize((new_width, new_height), Image.ANTIALIAS)
    #img.save(target_file_with_type)
    
    makeThumb(target_file_with_type, target_file_with_type, pad=False)

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
    
if __name__ == "__main__":
  main()