class environ() {
  file { "/home/vagrant/.bashrc":
      source  => "puppet:///modules/environ/bashrc",
      owner   => "vagrant",
      group   => "vagrant",
      mode    => "755",
      require => User["vagrant"],
  }
  # needed for selenium testing
  if ! defined(Package['firefox']) { package { 'firefox': ensure => installed, } }
  if ! defined(Package['screen']) { package { 'screen': ensure => installed, } }
  if ! defined(Package['xvfb']) { package { 'xvfb': ensure => installed, } }
}
