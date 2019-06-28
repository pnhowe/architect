import logging
import subprocess

GIT_CMD = '/usr/bin/git'


class Git():
  def __init__( self, url, branch, dir ):
    self.url = url
    self.branch = branch
    self.dir = dir

  def _execute( self, args ):
    logging.debug( 'git: running "{0}"'.format( args ) )

    try:
      args = [ GIT_CMD, '-C', self.dir ] + args
      logging.debug( 'git: executing "{0}"'.format( args ) )
      proc = subprocess.Popen( args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT )
      ( stdout, _ ) = proc.communicate()
    except Exception as e:
      raise Exception( 'Exception {0} while executing "{1}"'.format( e, args ) )

    stdout = stdout.decode()
    logging.debug( 'git: rc: {0}'.format( proc.returncode ) )
    logging.debug( 'git: output:\n----------\n{0}\n---------'.format( stdout ) )

    if proc.returncode != 0:
      raise Exception( 'git returned "{0}"'.format( proc.returncode ) )

    result = []
    for line in stdout.strip().splitlines():
      result.append( line.strip() )

    return result

  def checkout( self ):
    self._execute( [ 'clone', self.url, self.local_dir ] )

  def update( self ):
    self._execute( [ 'pull', 'origin', '{0}:master'.format( self.branch ) ] )

  def local_hash( self ):
    return self._execute( [ 'rev-parse', 'HEAD' ] )[ 0 ]

  def remote_hash( self ):
    return self._execute( [ 'ls-remote', 'origin', 'HEAD' ] )[ 0 ].split( "\t" )[ 0 ]
