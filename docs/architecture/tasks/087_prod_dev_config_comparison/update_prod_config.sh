#!/bin/bash

# 🔧 Production Configuration Update Script
# Task 087: Safely update production configuration with missing variables

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

# Configuration
PROD_SERVER="165.227.38.1"
SSH_KEY="~/.ssh/do_personal_assistant"
SSH_USER="deploy"
PROD_PROJECT_DIR="/home/deploy/ai_assistant"
LOCAL_PROJECT_DIR="/Users/ianleblanc/Desktop/personal_assistant"

# Backup directory
BACKUP_DIR="./backups/$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"

# Functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_step() {
    echo -e "${PURPLE}[STEP]${NC} $1"
}

# Function to backup production file
backup_prod_file() {
    local prod_file="$1"
    local backup_file="$BACKUP_DIR/$(basename "$prod_file")_backup_$(date +%Y%m%d_%H%M%S)"
    
    log_step "Backing up production file: $prod_file"
    
    ssh -i "$SSH_KEY" "$SSH_USER@$PROD_SERVER" "cat '$prod_file'" > "$backup_file" 2>/dev/null || {
        log_error "Failed to backup production file: $prod_file"
        return 1
    }
    
    log_success "Backup created: $backup_file"
    return 0
}

# Function to update production file with missing variables
update_prod_file() {
    local prod_file="$1"
    local missing_vars_file="$2"
    local update_log="$BACKUP_DIR/update_log_$(basename "$prod_file")_$(date +%Y%m%d_%H%M%S).txt"
    
    log_step "Updating production file: $prod_file"
    
    # Create update log
    echo "Production Configuration Update Log" > "$update_log"
    echo "File: $prod_file" >> "$update_log"
    echo "Generated: $(date)" >> "$update_log"
    echo "=================================" >> "$update_log"
    echo "" >> "$update_log"
    
    # Get current production file content
    local temp_prod="/tmp/current_prod_$(basename "$prod_file")"
    ssh -i "$SSH_KEY" "$SSH_USER@$PROD_SERVER" "cat '$prod_file'" > "$temp_prod" 2>/dev/null || {
        log_error "Failed to retrieve current production file: $prod_file"
        return 1
    }
    
    # Extract missing variables
    local missing_vars="/tmp/missing_vars_$(basename "$prod_file")"
    grep -E '^[A-Z_]+=' "$missing_vars_file" > "$missing_vars" || {
        log_warning "No missing variables found in: $missing_vars_file"
        return 0
    }
    
    # Create updated file
    local updated_file="/tmp/updated_prod_$(basename "$prod_file")"
    cp "$temp_prod" "$updated_file"
    
    # Add missing variables
    echo "" >> "$updated_file"
    echo "# Added variables from development environment - $(date)" >> "$updated_file"
    echo "" >> "$updated_file"
    
    while read -r line; do
        if [[ "$line" =~ ^[A-Z_]+= ]]; then
            local var_name=$(echo "$line" | cut -d'=' -f1)
            local var_value=$(echo "$line" | cut -d'=' -f2-)
            
            # Check if variable already exists
            if grep -q "^$var_name=" "$updated_file"; then
                log_warning "Variable $var_name already exists in production file"
                echo "SKIPPED: $line (already exists)" >> "$update_log"
            else
                # Add the variable
                echo "$line" >> "$updated_file"
                log_info "Added variable: $var_name"
                echo "ADDED: $line" >> "$update_log"
            fi
        fi
    done < "$missing_vars"
    
    # Show what will be added
    echo ""
    echo "Variables to be added to $prod_file:"
    echo "====================================="
    grep "^ADDED:" "$update_log" | sed 's/^ADDED: /  /'
    echo ""
    
    # Ask for confirmation
    read -p "Do you want to proceed with updating the production file? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        log_warning "Update cancelled by user"
        rm -f "$temp_prod" "$missing_vars" "$updated_file"
        return 1
    fi
    
    # Upload updated file to production
    log_step "Uploading updated file to production..."
    
    # Create a temporary file on production server
    local temp_remote="/tmp/updated_$(basename "$prod_file")_$(date +%s)"
    
    # Upload the updated file
    scp -i "$SSH_KEY" "$updated_file" "$SSH_USER@$PROD_SERVER:$temp_remote" || {
        log_error "Failed to upload updated file"
        rm -f "$temp_prod" "$missing_vars" "$updated_file"
        return 1
    }
    
    # Replace the original file
    ssh -i "$SSH_KEY" "$SSH_USER@$PROD_SERVER" "
        # Backup original file
        cp '$prod_file' '$prod_file.backup.$(date +%Y%m%d_%H%M%S)'
        # Replace with updated file
        mv '$temp_remote' '$prod_file'
        # Set proper permissions
        chmod 600 '$prod_file'
    " || {
        log_error "Failed to replace production file"
        return 1
    }
    
    log_success "Production file updated successfully: $prod_file"
    
    # Cleanup
    rm -f "$temp_prod" "$missing_vars" "$updated_file"
    
    return 0
}

# Function to validate production configuration
validate_prod_config() {
    local prod_file="$1"
    local validation_log="$BACKUP_DIR/validation_log_$(basename "$prod_file")_$(date +%Y%m%d_%H%M%S).txt"
    
    log_step "Validating production configuration: $prod_file"
    
    echo "Production Configuration Validation Log" > "$validation_log"
    echo "File: $prod_file" >> "$validation_log"
    echo "Generated: $(date)" >> "$validation_log"
    echo "=====================================" >> "$validation_log"
    echo "" >> "$validation_log"
    
    # Check if file exists and is readable
    ssh -i "$SSH_KEY" "$SSH_USER@$PROD_SERVER" "test -f '$prod_file' && test -r '$prod_file'" || {
        log_error "Production file not accessible: $prod_file"
        echo "ERROR: File not accessible" >> "$validation_log"
        return 1
    }
    
    # Check file syntax (basic validation)
    ssh -i "$SSH_KEY" "$SSH_USER@$PROD_SERVER" "
        # Check for basic syntax issues
        if grep -q '^[A-Z_]*=$' '$prod_file'; then
            echo 'WARNING: Found empty variables'
            grep -n '^[A-Z_]*=$' '$prod_file'
        fi
        
        # Check for duplicate variables
        if [ \$(grep -E '^[A-Z_]+=' '$prod_file' | cut -d'=' -f1 | sort | uniq -d | wc -l) -gt 0 ]; then
            echo 'WARNING: Found duplicate variables'
            grep -E '^[A-Z_]+=' '$prod_file' | cut -d'=' -f1 | sort | uniq -d
        fi
        
        # Count total variables
        echo 'Total variables: ' \$(grep -E '^[A-Z_]+=' '$prod_file' | wc -l)
    " >> "$validation_log" 2>&1
    
    log_success "Configuration validation completed: $prod_file"
    return 0
}

# Function to restart production services
restart_prod_services() {
    log_step "Restarting production services..."
    
    local restart_log="$BACKUP_DIR/restart_log_$(date +%Y%m%d_%H%M%S).txt"
    
    echo "Production Services Restart Log" > "$restart_log"
    echo "Generated: $(date)" >> "$restart_log"
    echo "=============================" >> "$restart_log"
    echo "" >> "$restart_log"
    
    # Restart services
    ssh -i "$SSH_KEY" "$SSH_USER@$PROD_SERVER" "
        cd $PROD_PROJECT_DIR
        
        echo 'Stopping services...' >> '$restart_log'
        docker-compose down >> '$restart_log' 2>&1 || echo 'Warning: docker-compose down failed' >> '$restart_log'
        
        echo 'Starting services...' >> '$restart_log'
        docker-compose up -d >> '$restart_log' 2>&1 || echo 'Error: docker-compose up failed' >> '$restart_log'
        
        echo 'Checking service status...' >> '$restart_log'
        docker-compose ps >> '$restart_log' 2>&1
        
        echo 'Service restart completed at: ' \$(date) >> '$restart_log'
    " || {
        log_error "Failed to restart production services"
        return 1
    }
    
    log_success "Production services restarted"
    return 0
}

# Function to test production endpoints
test_prod_endpoints() {
    log_step "Testing production endpoints..."
    
    local test_log="$BACKUP_DIR/endpoint_test_log_$(date +%Y%m%d_%H%M%S).txt"
    
    echo "Production Endpoint Test Log" > "$test_log"
    echo "Generated: $(date)" >> "$test_log"
    echo "==========================" >> "$test_log"
    echo "" >> "$test_log"
    
    # Test main endpoints
    local endpoints=(
        "https://ianleblanc.ca"
        "https://ianleblanc.ca/api/health"
        "https://ianleblanc.ca/api/v1/auth/status"
    )
    
    for endpoint in "${endpoints[@]}"; do
        echo "Testing: $endpoint" >> "$test_log"
        if curl -s -o /dev/null -w "%{http_code}" "$endpoint" >> "$test_log" 2>&1; then
            log_success "Endpoint accessible: $endpoint"
        else
            log_warning "Endpoint may have issues: $endpoint"
        fi
        echo "" >> "$test_log"
    done
    
    log_success "Endpoint testing completed"
    return 0
}

# Main update function
main() {
    log_info "Starting Production Configuration Update..."
    log_info "Task 087: Safely update production with missing variables"
    
    # Check if comparison results exist
    if [ ! -d "./comparison_results" ]; then
        log_error "Comparison results not found. Please run compare_config_files.sh first."
        exit 1
    fi
    
    # Find missing variables files
    local missing_files=($(find "./comparison_results" -name "*_missing_variables.txt"))
    
    if [ ${#missing_files[@]} -eq 0 ]; then
        log_warning "No missing variables files found. Nothing to update."
        exit 0
    fi
    
    log_info "Found ${#missing_files[@]} missing variables files:"
    for file in "${missing_files[@]}"; do
        echo "  - $file"
    done
    
    echo ""
    read -p "Do you want to proceed with updating production configuration? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        log_warning "Update cancelled by user"
        exit 0
    fi
    
    # Process each missing variables file
    for missing_file in "${missing_files[@]}"; do
        local comparison_name=$(basename "$missing_file" "_missing_variables.txt")
        local prod_file=""
        
        # Determine production file path based on comparison name
        case "$comparison_name" in
            "dev_vs_prod_env"|"local_prod_template_vs_actual_prod")
                prod_file="$PROD_PROJECT_DIR/config/production.env"
                ;;
            "docker_env_template_vs_prod")
                prod_file="$PROD_PROJECT_DIR/docker/.env.prod"
                ;;
            "docker_env_stage_template_vs_prod")
                prod_file="$PROD_PROJECT_DIR/docker/.env.stage"
                ;;
            *)
                log_warning "Unknown comparison type: $comparison_name"
                continue
                ;;
        esac
        
        log_info "Processing: $comparison_name -> $prod_file"
        
        # Backup production file
        if ! backup_prod_file "$prod_file"; then
            log_error "Failed to backup production file: $prod_file"
            continue
        fi
        
        # Update production file
        if ! update_prod_file "$prod_file" "$missing_file"; then
            log_error "Failed to update production file: $prod_file"
            continue
        fi
        
        # Validate updated configuration
        validate_prod_config "$prod_file"
    done
    
    # Ask if user wants to restart services
    echo ""
    read -p "Do you want to restart production services to apply changes? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        restart_prod_services
        test_prod_endpoints
    else
        log_warning "Services not restarted. Changes will take effect on next restart."
    fi
    
    log_success "Production configuration update completed!"
    log_info "Backups saved to: $BACKUP_DIR/"
    log_info "Update logs saved to: $BACKUP_DIR/"
    
    echo ""
    echo "=== UPDATE SUMMARY ==="
    echo "Backup directory: $BACKUP_DIR"
    echo "Files updated: ${#missing_files[@]}"
    echo "Services restarted: $([[ $REPLY =~ ^[Yy]$ ]] && echo "Yes" || echo "No")"
}

# Run main function
main "$@"
