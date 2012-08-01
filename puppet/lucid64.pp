class lucid64 {
  # setup base
  class { 'base': }
  # the config module loads the roles and envs for the node
  # in this case "vagrant" for both (which is set by the vagrant provisioning script)
  # the config module will handle pulling in the rest of the modules
  class { 'config': require => Class['base'], }
}

class { "lucid64": }
