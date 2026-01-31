from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Azure OpenAI
    azure_openai_endpoint: str = Field(..., env="AZURE_OPENAI_ENDPOINT")
    azure_openai_api_key: str = Field(..., env="AZURE_OPENAI_API_KEY")
    azure_openai_deployment: str = Field(..., env="AZURE_OPENAI_DEPLOYMENT")
    azure_openai_api_version: str = Field(..., env="AZURE_OPENAI_API_VERSION")

    # Data & storage
    database_url: str = Field(..., env="DATABASE_URL")
    redis_url: str = Field(..., env="REDIS_URL")
    cosmos_endpoint: str = Field(..., env="COSMOS_ENDPOINT")
    cosmos_key: str = Field(..., env="COSMOS_KEY")
    cosmos_database: str = Field(..., env="COSMOS_DATABASE")
    datalake_account_url: str = Field(..., env="DATALAKE_ACCOUNT_URL")

    # Azure Service Bus
    azure_service_bus_connection_string: str = Field(
        ..., env="AZURE_SERVICE_BUS_CONNECTION_STRING"
    )
    service_bus_namespace: str | None = Field(default=None, env="SERVICE_BUS_NAMESPACE")
    service_bus_queue_name: str | None = Field(default=None, env="SERVICE_BUS_QUEUE_NAME")
    service_bus_connection_string: str | None = Field(
        default=None, env="SERVICE_BUS_CONNECTION_STRING"
    )

    # Identity / MSAL
    msal_client_id: str = Field(..., env="MSAL_CLIENT_ID")
    azure_tenant_id: str = Field(..., env="AZURE_TENANT_ID")
    azure_client_secret: str = Field(..., env="AZURE_CLIENT_SECRET")

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False)


settings = Settings()
