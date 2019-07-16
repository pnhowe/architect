import os

from architect.Plan.lib import validate

ROOT_DIR = os.path.dirname( os.path.abspath( __file__ ) )


def validate_parser():
  search_path = [ os.path.join( ROOT_DIR, 'includes' ) ]
  validate( os.path.join( ROOT_DIR, 'project1' ), search_path )
