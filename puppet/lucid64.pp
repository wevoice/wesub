class lucid64 {
  include base
  class { 'appserver':
    python  => true,
    nodejs  => false,
  }
  include celery
  include closure
  include nginx
  include rabbitmq
  include redis
  include solr
  include mysql
  class { 'config':
    require => [
      Class['appserver'],
      Class['celery'],
      Class['closure'],
      Class['nginx'],
      Class['solr'],
      Class['mysql'],
      Class['rabbitmq'],
      Class['redis'],
    ],
  }
}

class { "lucid64": }
