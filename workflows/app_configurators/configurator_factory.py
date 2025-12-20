"""Factory for creating application configurators"""
from typing import List
from .apache_configurator import ApacheConfigurator
from .nginx_configurator import NginxConfigurator
from .php_configurator import PhpConfigurator
from .python_configurator import PythonConfigurator
from .nodejs_configurator import NodeJSConfigurator, NodeJSMinimalConfigurator
from .docker_configurator import DockerConfigurator
from .database_configurator import DatabaseConfigurator

class ConfiguratorFactory:
    """Factory for creating the appropriate configurators based on installed dependencies"""
    
    @staticmethod
    def create_configurators(client, config, installed_dependencies: List[str]):
        """
        Create configurators based on installed dependencies
        
        Args:
            client: LightsailBase client instance
            config: DeploymentConfig instance
            installed_dependencies: List of installed dependency names
            
        Returns:
            List of configurator instances
        """
        configurators = []
        
        # Web server configurators
        if 'apache' in installed_dependencies:
            configurators.append(ApacheConfigurator(client, config))
        
        if 'nginx' in installed_dependencies:
            configurators.append(NginxConfigurator(client, config))
        
        # Language/runtime configurators
        if 'php' in installed_dependencies:
            configurators.append(PhpConfigurator(client, config))
        
        if 'python' in installed_dependencies:
            configurators.append(PythonConfigurator(client, config))
        
        if 'nodejs' in installed_dependencies:
            # Check if Node.js configurator should be skipped
            if not config.should_skip_nodejs_configurator():
                configurators.append(NodeJSConfigurator(client, config))
            else:
                print("ℹ️  Skipping Node.js configurator as requested in configuration")
                # Still install Node.js and dependencies, but skip service creation
                from .nodejs_configurator import NodeJSMinimalConfigurator
                configurators.append(NodeJSMinimalConfigurator(client, config))
        
        # Database configurator (handles MySQL, PostgreSQL, RDS)
        mysql_enabled = config.get('dependencies.mysql.enabled', False)
        postgresql_enabled = config.get('dependencies.postgresql.enabled', False)
        
        if mysql_enabled or postgresql_enabled or 'mysql' in installed_dependencies or 'postgresql' in installed_dependencies:
            configurators.append(DatabaseConfigurator(client, config))
        
        # Docker configurator
        if 'docker' in installed_dependencies:
            configurators.append(DockerConfigurator(client, config))
        
        return configurators
    
    @staticmethod
    def get_docker_configurator(client, config):
        """Get Docker configurator specifically for Docker deployments"""
        return DockerConfigurator(client, config)
