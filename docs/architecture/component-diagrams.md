# Component Diagrams

This document provides comprehensive architectural diagrams for the Personal Assistant TDAH system, covering all aspects from high-level system overview to detailed component relationships.

## Table of Contents

- [C4 Model Diagrams](#c4-model-diagrams)
- [MAE_MAS Style Diagrams](#mae_mas-style-diagrams)
- [Technical Diagrams](#technical-diagrams)
- [Diagram Specifications](#diagram-specifications)

## C4 Model Diagrams

### 1. Context Diagram

```mermaid
graph TB
    User[👤 Users]
    Admin[👨‍💼 Administrators]
    Mobile[📱 Mobile Apps]
    Web[🌐 Web Applications]

    User --> PA[Personal Assistant System]
    Admin --> PA
    Mobile --> PA
    Web --> PA

    PA --> Google[🔍 Google Services]
    PA --> Microsoft[🏢 Microsoft Services]
    PA --> Notion[📝 Notion]
    PA --> YouTube[📺 YouTube]
    PA --> Twilio[📱 Twilio SMS]

    Google --> PA
    Microsoft --> PA
    Notion --> PA
    YouTube --> PA
    Twilio --> PA
```

### 2. Container Diagram

```mermaid
graph TB
    subgraph "Client Layer"
        WebApp[React Web App]
        MobileApp[Mobile App]
    end

    subgraph "API Gateway"
        Nginx[Nginx Load Balancer]
        FastAPI[FastAPI Application]
    end

    subgraph "Core Services"
        Auth[Authentication Service]
        Chat[Chat Service]
        OAuth[OAuth Service]
        SMS[SMS Router Service]
        Analytics[Analytics Service]
    end

    subgraph "Data Layer"
        PostgreSQL[(PostgreSQL Database)]
        Redis[(Redis Cache)]
    end

    subgraph "External Services"
        GoogleAPI[Google APIs]
        TwilioAPI[Twilio API]
    end

    WebApp --> Nginx
    MobileApp --> Nginx
    Nginx --> FastAPI
    FastAPI --> Auth
    FastAPI --> Chat
    FastAPI --> OAuth
    FastAPI --> SMS
    FastAPI --> Analytics

    Auth --> PostgreSQL
    Chat --> PostgreSQL
    OAuth --> PostgreSQL
    SMS --> PostgreSQL
    Analytics --> PostgreSQL

    Auth --> Redis
    Chat --> Redis
    OAuth --> Redis
    SMS --> Redis
    Analytics --> Redis

    OAuth --> GoogleAPI
    SMS --> TwilioAPI
```

### 3. Component Diagram

```mermaid
graph TB
    subgraph "FastAPI Application"
        subgraph "Authentication Module"
            AuthRouter[Auth Router]
            MFARouter[MFA Router]
            SessionRouter[Session Router]
            RBACRouter[RBAC Router]
        end

        subgraph "User Management Module"
            UserRouter[User Router]
            ProfileService[Profile Service]
            PreferenceService[Preference Service]
        end

        subgraph "Chat Module"
            ChatRouter[Chat Router]
            ChatService[Chat Service]
            AgentCore[Agent Core]
            ToolRegistry[Tool Registry]
        end

        subgraph "OAuth Module"
            OAuthRouter[OAuth Router]
            OAuthService[OAuth Service]
            TokenManager[Token Manager]
        end

        subgraph "SMS Module"
            SMSRouter[SMS Router]
            SMSRoutingEngine[SMS Routing Engine]
            TwilioService[Twilio Service]
        end

        subgraph "Analytics Module"
            AnalyticsRouter[Analytics Router]
            AnalyticsService[Analytics Service]
            CostCalculator[Cost Calculator]
        end
    end

    AuthRouter --> AuthService[Authentication Service]
    MFARouter --> MFAService[MFA Service]
    SessionRouter --> SessionService[Session Service]
    RBACRouter --> PermissionService[Permission Service]

    UserRouter --> UserService[User Service]
    ChatRouter --> ChatService
    OAuthRouter --> OAuthService
    SMSRouter --> SMSRoutingEngine
    AnalyticsRouter --> AnalyticsService
```

### 4. Code Diagram

```mermaid
graph TB
    subgraph "Authentication Package"
        AuthModels[Auth Models]
        AuthService[Auth Service]
        AuthRouter[Auth Router]
        AuthMiddleware[Auth Middleware]
    end

    subgraph "Database Package"
        DatabaseModels[Database Models]
        DatabaseSession[Database Session]
        DatabaseMigrations[Database Migrations]
    end

    subgraph "Tools Package"
        ToolRegistry[Tool Registry]
        WebSearchTool[Web Search Tool]
        FileTool[File Tool]
        EmailTool[Email Tool]
    end

    AuthRouter --> AuthService
    AuthService --> AuthModels
    AuthService --> DatabaseSession
    AuthRouter --> AuthMiddleware

    DatabaseSession --> DatabaseModels
    DatabaseSession --> DatabaseMigrations

    ToolRegistry --> WebSearchTool
    ToolRegistry --> FileTool
    ToolRegistry --> EmailTool
```

## MAE_MAS Style Diagrams

### 5. System Architecture Diagram

```mermaid
graph TB
    subgraph "Presentation Layer"
        WebUI[Web User Interface]
        MobileUI[Mobile User Interface]
        AdminUI[Admin Interface]
    end

    subgraph "Application Layer"
        APIGateway[API Gateway]
        AuthService[Authentication Service]
        ChatService[Chat Service]
        UserService[User Service]
        OAuthService[OAuth Service]
        SMSService[SMS Service]
        AnalyticsService[Analytics Service]
    end

    subgraph "Business Logic Layer"
        AgentCore[AI Agent Core]
        ToolRegistry[Tool Registry]
        PermissionEngine[Permission Engine]
        SessionManager[Session Manager]
        IntegrationManager[Integration Manager]
    end

    subgraph "Data Access Layer"
        DatabaseAccess[Database Access Layer]
        CacheAccess[Cache Access Layer]
        ExternalAPIs[External API Clients]
    end

    subgraph "Data Layer"
        PostgreSQL[(PostgreSQL)]
        Redis[(Redis Cache)]
        FileStorage[File Storage]
    end

    WebUI --> APIGateway
    MobileUI --> APIGateway
    AdminUI --> APIGateway

    APIGateway --> AuthService
    APIGateway --> ChatService
    APIGateway --> UserService
    APIGateway --> OAuthService
    APIGateway --> SMSService
    APIGateway --> AnalyticsService

    ChatService --> AgentCore
    AgentCore --> ToolRegistry
    AuthService --> PermissionEngine
    AuthService --> SessionManager
    OAuthService --> IntegrationManager

    AuthService --> DatabaseAccess
    ChatService --> DatabaseAccess
    UserService --> DatabaseAccess
    OAuthService --> DatabaseAccess
    SMSService --> DatabaseAccess
    AnalyticsService --> DatabaseAccess

    DatabaseAccess --> PostgreSQL
    CacheAccess --> Redis
    ExternalAPIs --> FileStorage
```

### 6. Network Architecture Diagram

```mermaid
graph TB
    subgraph "Internet"
        Users[Users]
        ExternalAPIs[External APIs]
    end

    subgraph "CDN Layer"
        CloudFlare[CloudFlare CDN]
    end

    subgraph "Load Balancer Layer"
        LoadBalancer[Load Balancer]
    end

    subgraph "Application Layer"
        WebServer1[Web Server 1]
        WebServer2[Web Server 2]
        WebServer3[Web Server 3]
    end

    subgraph "Database Layer"
        PrimaryDB[(Primary Database)]
        ReadReplica1[(Read Replica 1)]
        ReadReplica2[(Read Replica 2)]
    end

    subgraph "Cache Layer"
        RedisCluster[Redis Cluster]
    end

    Users --> CloudFlare
    ExternalAPIs --> CloudFlare
    CloudFlare --> LoadBalancer
    LoadBalancer --> WebServer1
    LoadBalancer --> WebServer2
    LoadBalancer --> WebServer3

    WebServer1 --> PrimaryDB
    WebServer2 --> PrimaryDB
    WebServer3 --> PrimaryDB

    WebServer1 --> ReadReplica1
    WebServer2 --> ReadReplica2
    WebServer3 --> ReadReplica1

    WebServer1 --> RedisCluster
    WebServer2 --> RedisCluster
    WebServer3 --> RedisCluster

    PrimaryDB --> ReadReplica1
    PrimaryDB --> ReadReplica2
```

### 7. Multi-User Data Flow Diagram

```mermaid
sequenceDiagram
    participant U1 as User 1
    participant U2 as User 2
    participant API as API Gateway
    participant Auth as Auth Service
    participant Chat as Chat Service
    participant DB as Database
    participant Cache as Redis Cache

    U1->>API: Login Request
    API->>Auth: Authenticate User 1
    Auth->>DB: Validate Credentials
    Auth->>Cache: Store Session
    Auth-->>API: JWT Token (User 1)
    API-->>U1: Authentication Success

    U2->>API: Login Request
    API->>Auth: Authenticate User 2
    Auth->>DB: Validate Credentials
    Auth->>Cache: Store Session
    Auth-->>API: JWT Token (User 2)
    API-->>U2: Authentication Success

    U1->>API: Send Chat Message
    API->>Chat: Process Message (User 1)
    Chat->>DB: Store Message (User 1)
    Chat-->>API: Response (User 1)
    API-->>U1: Chat Response

    U2->>API: Send Chat Message
    API->>Chat: Process Message (User 2)
    Chat->>DB: Store Message (User 2)
    Chat-->>API: Response (User 2)
    API-->>U2: Chat Response

    Note over DB: User data is completely isolated
    Note over Cache: Sessions are user-specific
```

### 8. OAuth Progressive Integration Diagram

```mermaid
graph TB
    subgraph "User Journey"
        Start[User Starts OAuth]
        Provider[Choose Provider]
        Authorize[Authorize Application]
        Callback[Handle Callback]
        Integration[Integration Active]
    end

    subgraph "System Flow"
        Initiate[Initiate OAuth]
        StoreState[Store State]
        Redirect[Redirect to Provider]
        Exchange[Exchange Code]
        StoreToken[Store Tokens]
        Sync[Sync Data]
    end

    subgraph "Providers"
        Google[Google APIs]
        Microsoft[Microsoft APIs]
        Notion[Notion APIs]
        YouTube[YouTube APIs]
    end

    Start --> Initiate
    Initiate --> StoreState
    StoreState --> Redirect
    Redirect --> Provider
    Provider --> Authorize
    Authorize --> Callback
    Callback --> Exchange
    Exchange --> StoreToken
    StoreToken --> Integration
    Integration --> Sync

    Exchange --> Google
    Exchange --> Microsoft
    Exchange --> Notion
    Exchange --> YouTube
```

### 9. SMS Routing Architecture Diagram

```mermaid
graph TB
    subgraph "SMS Flow"
        IncomingSMS[Incoming SMS]
        TwilioWebhook[Twilio Webhook]
        SMSRouter[SMS Router Service]
        UserMapping[User Mapping]
        DeliveryStatus[Delivery Status]
    end

    subgraph "Routing Logic"
        PhoneLookup[Phone Number Lookup]
        UserIdentification[User Identification]
        MessageRouting[Message Routing]
        StatusUpdate[Status Update]
    end

    subgraph "Data Storage"
        PhoneMappings[(Phone Mappings)]
        SMSLogs[(SMS Logs)]
        UserProfiles[(User Profiles)]
    end

    IncomingSMS --> TwilioWebhook
    TwilioWebhook --> SMSRouter
    SMSRouter --> PhoneLookup
    PhoneLookup --> UserIdentification
    UserIdentification --> MessageRouting
    MessageRouting --> DeliveryStatus

    PhoneLookup --> PhoneMappings
    UserIdentification --> UserProfiles
    MessageRouting --> SMSLogs
    StatusUpdate --> SMSLogs
```

### 10. Security Architecture Diagram

```mermaid
graph TB
    subgraph "Security Layers"
        subgraph "Authentication Layer"
            JWT[JWT Tokens]
            MFA[Multi-Factor Auth]
            Session[Session Management]
        end

        subgraph "Authorization Layer"
            RBAC[Role-Based Access Control]
            Permissions[Permission Engine]
            Audit[Audit Logging]
        end

        subgraph "Data Protection Layer"
            Encryption[Data Encryption]
            Isolation[User Data Isolation]
            Backup[Secure Backups]
        end

        subgraph "Network Security Layer"
            TLS[TLS Encryption]
            Firewall[Firewall Rules]
            VPN[VPN Access]
        end
    end

    subgraph "Security Services"
        AuthService[Authentication Service]
        PermissionService[Permission Service]
        AuditService[Audit Service]
        SecurityMonitor[Security Monitor]
    end

    JWT --> AuthService
    MFA --> AuthService
    Session --> AuthService

    RBAC --> PermissionService
    Permissions --> PermissionService
    Audit --> AuditService

    Encryption --> SecurityMonitor
    Isolation --> SecurityMonitor
    Backup --> SecurityMonitor

    TLS --> SecurityMonitor
    Firewall --> SecurityMonitor
    VPN --> SecurityMonitor
```

## Technical Diagrams

### 11. Entity Relationship Diagram (ERD)

```mermaid
erDiagram
    USERS {
        int id PK
        string email UK
        string password_hash
        string first_name
        string last_name
        string phone_number
        boolean email_verified
        boolean phone_verified
        boolean mfa_enabled
        datetime created_at
        datetime updated_at
    }

    ROLES {
        int id PK
        string name UK
        string description
        int parent_role_id FK
        datetime created_at
        datetime updated_at
    }

    PERMISSIONS {
        int id PK
        string name UK
        string resource_type
        string action
        string description
        datetime created_at
    }

    USER_ROLES {
        int id PK
        int user_id FK
        int role_id FK
        boolean is_primary
        int granted_by FK
        datetime granted_at
        datetime expires_at
    }

    CONVERSATIONS {
        int id PK
        string conversation_id UK
        int user_id FK
        string user_input
        json focus_areas
        int step_count
        json last_tool_result
        datetime created_at
        datetime updated_at
    }

    CONVERSATION_MESSAGES {
        int id PK
        string conversation_id FK
        string role
        string content
        string message_type
        string tool_name
        string tool_success
        datetime timestamp
        json additional_data
    }

    OAUTH_INTEGRATIONS {
        int id PK
        int user_id FK
        string provider
        string provider_user_id
        string access_token
        string refresh_token
        json scopes
        datetime expires_at
        datetime created_at
        datetime updated_at
    }

    SMS_LOGS {
        int id PK
        int user_id FK
        string phone_number
        string message_content
        string direction
        string status
        string twilio_sid
        datetime created_at
    }

    USERS ||--o{ USER_ROLES : has
    ROLES ||--o{ USER_ROLES : assigned_to
    USERS ||--o{ CONVERSATIONS : creates
    CONVERSATIONS ||--o{ CONVERSATION_MESSAGES : contains
    USERS ||--o{ OAUTH_INTEGRATIONS : has
    USERS ||--o{ SMS_LOGS : generates
```

### 12. API Endpoint Diagram

```mermaid
graph TB
    subgraph "API Endpoints"
        subgraph "Authentication"
            POST_auth_register[POST /auth/register]
            POST_auth_login[POST /auth/login]
            POST_auth_refresh[POST /auth/refresh]
            POST_auth_logout[POST /auth/logout]
            GET_auth_me[GET /auth/me]
        end

        subgraph "User Management"
            GET_users[GET /users]
            GET_users_id[GET /users/{id}]
            PUT_users_id[PUT /users/{id}]
            GET_users_me[GET /users/me]
            PUT_users_me[PUT /users/me]
        end

        subgraph "Chat"
            POST_chat_messages[POST /chat/messages]
            GET_chat_conversations[GET /chat/conversations]
            GET_chat_conversations_id[GET /chat/conversations/{id}]
            DELETE_chat_conversations_id[DELETE /chat/conversations/{id}]
        end

        subgraph "OAuth"
            GET_oauth_providers[GET /oauth/providers]
            POST_oauth_initiate[POST /oauth/initiate]
            POST_oauth_callback[POST /oauth/callback]
            GET_oauth_integrations[GET /oauth/integrations]
        end

        subgraph "SMS Router"
            POST_sms_webhook[POST /sms-router/webhook/sms]
            POST_sms_delivery[POST /sms-router/webhook/delivery-status]
            GET_sms_status[GET /sms-router/admin/status]
        end

        subgraph "Analytics"
            GET_analytics_me[GET /analytics/me/sms-analytics]
            GET_analytics_costs[GET /analytics/me/sms-costs]
            GET_analytics_report[GET /analytics/me/sms-usage-report]
        end
    end
```

### 13. Frontend Component Hierarchy Diagram

```mermaid
graph TB
    subgraph "React Application"
        App[App Component]

        subgraph "Layout Components"
            Header[Header]
            Sidebar[Sidebar]
            Footer[Footer]
            MainContent[Main Content]
        end

        subgraph "Authentication Components"
            LoginForm[Login Form]
            RegisterForm[Register Form]
            MFAForm[MFA Form]
            PasswordReset[Password Reset]
        end

        subgraph "Chat Components"
            ChatInterface[Chat Interface]
            MessageList[Message List]
            MessageInput[Message Input]
            ConversationList[Conversation List]
        end

        subgraph "User Management Components"
            ProfileForm[Profile Form]
            PreferencesForm[Preferences Form]
            PhoneNumberForm[Phone Number Form]
            SessionManager[Session Manager]
        end

        subgraph "OAuth Components"
            OAuthProvider[OAuth Provider]
            IntegrationList[Integration List]
            IntegrationCard[Integration Card]
            OAuthCallback[OAuth Callback]
        end

        subgraph "Analytics Components"
            AnalyticsDashboard[Analytics Dashboard]
            UsageChart[Usage Chart]
            CostChart[Cost Chart]
            ReportGenerator[Report Generator]
        end

        App --> Header
        App --> Sidebar
        App --> MainContent
        App --> Footer

        MainContent --> LoginForm
        MainContent --> RegisterForm
        MainContent --> ChatInterface
        MainContent --> ProfileForm
        MainContent --> OAuthProvider
        MainContent --> AnalyticsDashboard

        ChatInterface --> MessageList
        ChatInterface --> MessageInput
        ChatInterface --> ConversationList

        ProfileForm --> PreferencesForm
        ProfileForm --> PhoneNumberForm
        ProfileForm --> SessionManager

        OAuthProvider --> IntegrationList
        IntegrationList --> IntegrationCard
        OAuthProvider --> OAuthCallback

        AnalyticsDashboard --> UsageChart
        AnalyticsDashboard --> CostChart
        AnalyticsDashboard --> ReportGenerator
    end
```

### 14. Deployment Architecture Diagram

```mermaid
graph TB
    subgraph "Production Environment"
        subgraph "Load Balancer Layer"
            LB[Load Balancer]
        end

        subgraph "Application Layer"
            App1[App Instance 1]
            App2[App Instance 2]
            App3[App Instance 3]
        end

        subgraph "Database Layer"
            PrimaryDB[(Primary Database)]
            ReadReplica1[(Read Replica 1)]
            ReadReplica2[(Read Replica 2)]
        end

        subgraph "Cache Layer"
            Redis1[(Redis Node 1)]
            Redis2[(Redis Node 2)]
            Redis3[(Redis Node 3)]
        end

        subgraph "Storage Layer"
            FileStorage[File Storage]
            BackupStorage[Backup Storage]
        end

        subgraph "Monitoring Layer"
            Prometheus[Prometheus]
            Grafana[Grafana]
            Loki[Loki]
            AlertManager[Alert Manager]
        end
    end

    LB --> App1
    LB --> App2
    LB --> App3

    App1 --> PrimaryDB
    App2 --> PrimaryDB
    App3 --> PrimaryDB

    App1 --> ReadReplica1
    App2 --> ReadReplica2
    App3 --> ReadReplica1

    App1 --> Redis1
    App2 --> Redis2
    App3 --> Redis3

    App1 --> FileStorage
    App2 --> FileStorage
    App3 --> FileStorage

    PrimaryDB --> BackupStorage

    Prometheus --> App1
    Prometheus --> App2
    Prometheus --> App3
    Prometheus --> PrimaryDB
    Prometheus --> Redis1

    Grafana --> Prometheus
    Loki --> App1
    Loki --> App2
    Loki --> App3
    AlertManager --> Prometheus
```

### 15. Monitoring and Observability Diagram

```mermaid
graph TB
    subgraph "Application Layer"
        FastAPI[FastAPI App]
        React[React App]
        Celery[Celery Workers]
    end

    subgraph "Data Layer"
        PostgreSQL[(PostgreSQL)]
        Redis[(Redis)]
    end

    subgraph "Monitoring Stack"
        Prometheus[Prometheus]
        Grafana[Grafana]
        Loki[Loki]
        AlertManager[Alert Manager]
    end

    subgraph "Metrics Collection"
        AppMetrics[Application Metrics]
        SystemMetrics[System Metrics]
        BusinessMetrics[Business Metrics]
        CustomMetrics[Custom Metrics]
    end

    subgraph "Logging"
        AppLogs[Application Logs]
        AccessLogs[Access Logs]
        ErrorLogs[Error Logs]
        AuditLogs[Audit Logs]
    end

    subgraph "Alerting"
        EmailAlerts[Email Alerts]
        SlackAlerts[Slack Alerts]
        PagerDuty[PagerDuty]
        Dashboard[Dashboard Updates]
    end

    FastAPI --> AppMetrics
    React --> AppMetrics
    Celery --> AppMetrics
    PostgreSQL --> SystemMetrics
    Redis --> SystemMetrics

    AppMetrics --> Prometheus
    SystemMetrics --> Prometheus
    BusinessMetrics --> Prometheus
    CustomMetrics --> Prometheus

    FastAPI --> AppLogs
    React --> AccessLogs
    Celery --> ErrorLogs
    PostgreSQL --> AuditLogs

    AppLogs --> Loki
    AccessLogs --> Loki
    ErrorLogs --> Loki
    AuditLogs --> Loki

    Prometheus --> Grafana
    Loki --> Grafana
    Prometheus --> AlertManager

    AlertManager --> EmailAlerts
    AlertManager --> SlackAlerts
    AlertManager --> PagerDuty
    AlertManager --> Dashboard
```

### 16. CI/CD Pipeline Diagram

```mermaid
graph TB
    subgraph "Source Control"
        GitHub[GitHub Repository]
    end

    subgraph "CI/CD Pipeline"
        Trigger[Code Push Trigger]
        Build[Build Stage]
        Test[Test Stage]
        Security[Security Scan]
        Deploy[Deploy Stage]
    end

    subgraph "Build Process"
        DockerBuild[Docker Build]
        ImageScan[Image Scan]
        ImagePush[Push to Registry]
    end

    subgraph "Testing"
        UnitTests[Unit Tests]
        IntegrationTests[Integration Tests]
        E2ETests[E2E Tests]
        PerformanceTests[Performance Tests]
    end

    subgraph "Security"
        CodeScan[Code Scan]
        DependencyScan[Dependency Scan]
        SecretScan[Secret Scan]
        VulnerabilityScan[Vulnerability Scan]
    end

    subgraph "Deployment"
        StagingDeploy[Staging Deployment]
        ProductionDeploy[Production Deployment]
        Rollback[Rollback Capability]
    end

    GitHub --> Trigger
    Trigger --> Build
    Build --> Test
    Test --> Security
    Security --> Deploy

    Build --> DockerBuild
    DockerBuild --> ImageScan
    ImageScan --> ImagePush

    Test --> UnitTests
    Test --> IntegrationTests
    Test --> E2ETests
    Test --> PerformanceTests

    Security --> CodeScan
    Security --> DependencyScan
    Security --> SecretScan
    Security --> VulnerabilityScan

    Deploy --> StagingDeploy
    StagingDeploy --> ProductionDeploy
    ProductionDeploy --> Rollback
```

### 17. Data Flow Diagram

```mermaid
graph TB
    subgraph "User Input"
        UserAction[User Action]
        WebSocket[WebSocket Message]
        APIRequest[API Request]
    end

    subgraph "Processing Layer"
        APIGateway[API Gateway]
        AuthMiddleware[Auth Middleware]
        RateLimiter[Rate Limiter]
        RequestRouter[Request Router]
    end

    subgraph "Business Logic"
        ServiceLayer[Service Layer]
        BusinessRules[Business Rules]
        Validation[Validation]
        Processing[Data Processing]
    end

    subgraph "Data Access"
        Repository[Repository Layer]
        Cache[Cache Layer]
        Database[Database Layer]
        ExternalAPI[External API]
    end

    subgraph "Response"
        ResponseBuilder[Response Builder]
        ErrorHandler[Error Handler]
        Logging[Logging]
        UserResponse[User Response]
    end

    UserAction --> APIGateway
    WebSocket --> APIGateway
    APIRequest --> APIGateway

    APIGateway --> AuthMiddleware
    AuthMiddleware --> RateLimiter
    RateLimiter --> RequestRouter

    RequestRouter --> ServiceLayer
    ServiceLayer --> BusinessRules
    BusinessRules --> Validation
    Validation --> Processing

    Processing --> Repository
    Repository --> Cache
    Repository --> Database
    Repository --> ExternalAPI

    Cache --> ResponseBuilder
    Database --> ResponseBuilder
    ExternalAPI --> ResponseBuilder

    ResponseBuilder --> ErrorHandler
    ErrorHandler --> Logging
    Logging --> UserResponse
```

### 18. Security Flow Diagram

```mermaid
graph TB
    subgraph "Authentication Flow"
        LoginRequest[Login Request]
        CredentialCheck[Credential Check]
        MFACheck[MFA Check]
        TokenGeneration[Token Generation]
        SessionCreation[Session Creation]
    end

    subgraph "Authorization Flow"
        RequestAuth[Request Authorization]
        PermissionCheck[Permission Check]
        RoleCheck[Role Check]
        AccessGrant[Access Granted]
        AccessDeny[Access Denied]
    end

    subgraph "Data Protection"
        DataEncryption[Data Encryption]
        DataIsolation[Data Isolation]
        DataValidation[Data Validation]
        DataAudit[Data Audit]
    end

    subgraph "Security Monitoring"
        ThreatDetection[Threat Detection]
        AnomalyDetection[Anomaly Detection]
        SecurityAlert[Security Alert]
        IncidentResponse[Incident Response]
    end

    LoginRequest --> CredentialCheck
    CredentialCheck --> MFACheck
    MFACheck --> TokenGeneration
    TokenGeneration --> SessionCreation

    RequestAuth --> PermissionCheck
    PermissionCheck --> RoleCheck
    RoleCheck --> AccessGrant
    RoleCheck --> AccessDeny

    AccessGrant --> DataEncryption
    DataEncryption --> DataIsolation
    DataIsolation --> DataValidation
    DataValidation --> DataAudit

    DataAudit --> ThreatDetection
    ThreatDetection --> AnomalyDetection
    AnomalyDetection --> SecurityAlert
    SecurityAlert --> IncidentResponse
```

## Diagram Specifications

### Visual Standards

**Colors**

- Primary: #007bff (Blue)
- Success: #28a745 (Green)
- Warning: #ffc107 (Yellow)
- Danger: #dc3545 (Red)
- Info: #17a2b8 (Cyan)
- Light: #f8f9fa (Light Gray)
- Dark: #343a40 (Dark Gray)

**Shapes**

- Rectangles: Components and services
- Circles: Data stores and external systems
- Diamonds: Decision points
- Arrows: Data flow and relationships

**Typography**

- Headers: Bold, 16px
- Labels: Regular, 12px
- Descriptions: Regular, 10px

### Technical Standards

**Mermaid Syntax**

- Use consistent node naming
- Group related components
- Include proper relationships
- Add descriptive labels

**Content Standards**

- Clear component names
- Descriptive relationships
- Proper data flow direction
- Include external dependencies

### Maintenance Guidelines

**Version Control**

- Store diagrams in version control
- Include change documentation
- Maintain diagram history
- Review changes regularly

**Updates**

- Update diagrams with code changes
- Validate diagram accuracy
- Test diagram rendering
- Document diagram purpose

This comprehensive set of diagrams provides a complete visual representation of the Personal Assistant TDAH system architecture, from high-level system overview to detailed component relationships and data flows.
