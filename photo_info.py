import logging
from PIL import Image
import exifread


class PhotoInfo:
    def __init__(self, photo_name_full, thumb_size=50):
        self.photo_name_full = photo_name_full
        self.thumb_size = thumb_size

        self._load_thumbnail()

        self._define_useful_tags()
        self.metadata = None

    def get_metadata(self):
        if self.metadata is None:
            self._load_metadata()
        return self.metadata

    def _load_thumbnail(self):
        """resize the pic"""
        logg = logging.getLogger(f"c.{__class__.__name__}._load_metadata")
        logg.setLevel("TRACE")

        self.thumb = Image.open(self.photo_name_full)

        # also save the real dimensions
        self.width, self.height = self.thumb.size

        self.thumb.thumbnail((self.thumb_size, self.thumb_size), Image.BOX)
        # MAYBE lanczos is fast enough to be viable
        #  self.thumb.thumbnail((self.thumb_size, self.thumb_size), Image.LANCZOS)

    def _load_metadata(self):
        """Load metadata for Photo, according to useful list"""
        logg = logging.getLogger(f"c.{__class__.__name__}._load_metadata")
        logg.setLevel("TRACE")
        logg.trace(f"Loading metadata")

        with open(self.photo_name_full, "rb") as f:
            tags = exifread.process_file(f)

        # save only tags listed as useful
        self.metadata = {}
        for tag in tags:
            if tag in self._useful_tags:
                logg.trace(f"{tag}: {tags[tag]}")
                self.metadata[tag] = tags[tag]

        # add real dimensions as metadata
        logg.trace(f"Dimensions: {self.width} x {self.height}")
        self.metadata['PILWidth'] = self.width
        self.metadata['PILHeight'] = self.height

        #  for tag in tags.keys():
            #  if tag not in (
                #  "JPEGThumbnail",
                #  "TIFFThumbnail",
                #  "Filename",
                #  "EXIF MakerNote",
            #  ):
                #  print("Key: %s, value %s" % (tag, tags[tag]))

    def _define_useful_tags(self):
        """Populate set of useful tags"""
        self._useful_tags = set(
            [
                #  "JPEGThumbnail",
                #  "TIFFThumbnail",
                "Filename",
                #  'EXIF MakerNote',
                # 'Image Tag 0x000B',
                # 'Image ImageDescription',
                "Image Make",
                "Image Model",
                "Image Orientation",
                # 'Image XResolution',
                # 'Image YResolution',
                # 'Image ResolutionUnit',
                "Image Software",
                "Image DateTime",
                # 'Image YCbCrPositioning',
                # 'Image ExifOffset',
                # 'Image PrintIM',
                # 'Image Padding',
                "GPS GPSLatitudeRef",
                "GPS GPSLatitude",
                "GPS GPSLongitudeRef",
                "GPS GPSLongitude",
                # 'GPS GPSAltitudeRef',
                # 'GPS GPSTimeStamp',
                # 'GPS GPSSatellites',
                # 'GPS GPSImgDirectionRef',
                # 'GPS GPSMapDatum',
                # 'GPS GPSDate',
                # 'Image GPSInfo',
                # 'Thumbnail Compression',
                # 'Thumbnail XResolution',
                # 'Thumbnail YResolution',
                # 'Thumbnail ResolutionUnit',
                # 'Thumbnail JPEGInterchangeFormat',
                # 'Thumbnail JPEGInterchangeFormatLength',
                "EXIF ExposureTime",
                "EXIF FNumber",
                "EXIF ExposureProgram",
                "EXIF ISOSpeedRatings",
                "EXIF ExifVersion",
                "EXIF DateTimeOriginal",
                "EXIF DateTimeDigitized",
                # 'EXIF ComponentsConfiguration',
                # 'EXIF CompressedBitsPerPixel',
                # 'EXIF BrightnessValue',
                "EXIF ExposureBiasValue",
                # 'EXIF MaxApertureValue',
                # 'EXIF MeteringMode',
                # 'EXIF LightSource',
                "EXIF Flash",
                "EXIF FocalLength",
                # 'EXIF UserComment',
                # 'EXIF FlashPixVersion',
                # 'EXIF ColorSpace',
                "EXIF ExifImageWidth",
                "EXIF ExifImageLength",
                # 'Interoperability InteroperabilityVersion',
                # 'EXIF InteroperabilityOffset',
                # 'EXIF FileSource',
                # 'EXIF SceneType',
                # 'EXIF CustomRendered',
                "EXIF ExposureMode",
                "EXIF WhiteBalance",
                "EXIF DigitalZoomRatio",
                "EXIF FocalLengthIn35mmFilm",
            ]
        )
