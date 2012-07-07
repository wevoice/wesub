class lucid64 {
  include base
  class { 'appserver':
    python  => true,
    nodejs  => false,
  }
  include config
  include celery
  include nginx
  include rabbitmq
  include redis
  include solr
  include mysql
}

class { "lucid64": }
