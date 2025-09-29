#!/bin/bash

# 🔍 Production vs Development Config/Env Files Comparison Script
# Task 087: Direct SSH-based comparison of configuration files

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
PROD_SERVER="165.227.38.1"
SSH_KEY="~/.ssh/do_personal_assistant"
SSH_USER="deploy"
PROD_PROJECT_DIR="/home/deploy/ai_assistant"
LOCAL_PROJECT_DIR="/Users/ianleblanc/Desktop/personal_assistant"

# Output directory
OUTPUT_DIR="./comparison_results"
mkdir -p "$OUTPUT_DIR"

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

log_comparison() {
    echo -e "${CYAN}[COMPARE]${NC} $1"
}

# Function to test SSH connection
test_ssh_connection() {
    log_step "Testing SSH connection to production server..."
    
    if ssh -i "$SSH_KEY" -o ConnectTimeout=10 "$SSH_USER@$PROD_SERVER" "echo 'SSH connection successful'" 2>/dev/null; then
        log_success "SSH connection established"
        return 0
    else
        log_error "Failed to connect to production server"
        log_error "Please check:"
        log_error "  - SSH key exists: $SSH_KEY"
        log_error "  - Server is accessible: $PROD_SERVER"
        log_error "  - User has access: $SSH_USER"
        return 1
    fi
}

# Function to discover production environment files
discover_prod_files() {
    log_step "Discovering environment files in production..."
    
    local prod_files_file="$OUTPUT_DIR/prod_files_list.txt"
    
    # Get list of all environment files in production
    ssh -i "$SSH_KEY" "$SSH_USER@$PROD_SERVER" "
        find $PROD_PROJECT_DIR -name '*.env*' -o -name '.env*' | sort
    " > "$prod_files_file" 2>/dev/null || {
        log_warning "Could not discover production files"
        return 1
    }
    
    log_info "Found production environment files:"
    cat "$prod_files_file" | while read -r file; do
        echo "  - $file"
    done
    
    return 0
}

# Function to get production file content
get_prod_file_content() {
    local prod_file="$1"
    local output_file="$2"
    
    log_comparison "Retrieving: $prod_file"
    
    ssh -i "$SSH_KEY" "$SSH_USER@$PROD_SERVER" "cat '$prod_file'" > "$output_file" 2>/dev/null || {
        log_warning "Could not retrieve production file: $prod_file"
        return 1
    }
    
    return 0
}

# Function to compare environment files
compare_env_files() {
    local local_file="$1"
    local prod_file="$2"
    local comparison_name="$3"
    
    log_comparison "Comparing $comparison_name..."
    
    # Create temporary files for comparison
    local temp_local="/tmp/local_$(basename "$local_file")"
    local temp_prod="/tmp/prod_$(basename "$prod_file")"
    
    # Get production file content
    if ! get_prod_file_content "$prod_file" "$temp_prod"; then
        log_warning "Skipping comparison for $comparison_name - could not retrieve production file"
        return 1
    fi
    
    # Copy local file
    cp "$local_file" "$temp_local"
    
    # Compare files
    local diff_file="$OUTPUT_DIR/${comparison_name}_diff.txt"
    if diff -u "$temp_local" "$temp_prod" > "$diff_file" 2>&1; then
        log_success "$comparison_name files are identical"
        echo "✅ $comparison_name: No differences found" >> "$OUTPUT_DIR/summary.txt"
        rm -f "$diff_file"  # Remove empty diff file
    else
        log_warning "$comparison_name files differ"
        echo "⚠️  $comparison_name: Differences found - see ${comparison_name}_diff.txt" >> "$OUTPUT_DIR/summary.txt"
        
        # Generate detailed analysis
        echo "=== $comparison_name Analysis ===" >> "$OUTPUT_DIR/detailed_analysis.txt"
        echo "Local file: $local_file" >> "$OUTPUT_DIR/detailed_analysis.txt"
        echo "Production file: $prod_file" >> "$OUTPUT_DIR/detailed_analysis.txt"
        echo "Generated: $(date)" >> "$OUTPUT_DIR/detailed_analysis.txt"
        echo "" >> "$OUTPUT_DIR/detailed_analysis.txt"
        
        # Show differences
        echo "Differences:" >> "$OUTPUT_DIR/detailed_analysis.txt"
        cat "$diff_file" >> "$OUTPUT_DIR/detailed_analysis.txt"
        echo "" >> "$OUTPUT_DIR/detailed_analysis.txt"
        echo "=================================" >> "$OUTPUT_DIR/detailed_analysis.txt"
        echo "" >> "$OUTPUT_DIR/detailed_analysis.txt"
        
        # Extract missing variables
        extract_missing_variables "$temp_local" "$temp_prod" "$comparison_name"
    fi
    
    # Cleanup
    rm -f "$temp_local" "$temp_prod"
}

# Function to extract missing variables
extract_missing_variables() {
    local local_file="$1"
    local prod_file="$2"
    local comparison_name="$3"
    
    local missing_file="$OUTPUT_DIR/${comparison_name}_missing_variables.txt"
    
    echo "=== Missing Variables Analysis for $comparison_name ===" > "$missing_file"
    echo "Generated: $(date)" >> "$missing_file"
    echo "" >> "$missing_file"
    
    # Extract variables from local file
    grep -E '^[A-Z_]+=' "$local_file" | cut -d'=' -f1 | sort > "/tmp/local_vars_$comparison_name"
    
    # Extract variables from production file
    grep -E '^[A-Z_]+=' "$prod_file" | cut -d'=' -f1 | sort > "/tmp/prod_vars_$comparison_name"
    
    # Find variables in local but not in production
    comm -23 "/tmp/local_vars_$comparison_name" "/tmp/prod_vars_$comparison_name" > "/tmp/missing_vars_$comparison_name"
    
    if [ -s "/tmp/missing_vars_$comparison_name" ]; then
        echo "Variables present in local but missing in production:" >> "$missing_file"
        echo "" >> "$missing_file"
        while read -r var; do
            local value=$(grep "^$var=" "$local_file" | cut -d'=' -f2-)
            echo "$var=$value" >> "$missing_file"
        done < "/tmp/missing_vars_$comparison_name"
        echo "" >> "$missing_file"
    else
        echo "No missing variables found." >> "$missing_file"
    fi
    
    # Find variables in production but not in local
    comm -13 "/tmp/local_vars_$comparison_name" "/tmp/prod_vars_$comparison_name" > "/tmp/extra_vars_$comparison_name"
    
    if [ -s "/tmp/extra_vars_$comparison_name" ]; then
        echo "Variables present in production but not in local:" >> "$missing_file"
        echo "" >> "$missing_file"
        while read -r var; do
            local value=$(grep "^$var=" "$prod_file" | cut -d'=' -f2-)
            echo "$var=$value" >> "$missing_file"
        done < "/tmp/extra_vars_$comparison_name"
        echo "" >> "$missing_file"
    else
        echo "No extra variables found in production." >> "$missing_file"
    fi
    
    # Cleanup temp files
    rm -f "/tmp/local_vars_$comparison_name" "/tmp/prod_vars_$comparison_name" "/tmp/missing_vars_$comparison_name" "/tmp/extra_vars_$comparison_name"
}

# Function to check if production file exists
check_prod_file() {
    local file_path="$1"
    ssh -i "$SSH_KEY" "$SSH_USER@$PROD_SERVER" "test -f '$file_path'" 2>/dev/null
}

# Function to get production environment info
get_prod_env_info() {
    log_step "Gathering production environment information..."
    
    local info_file="$OUTPUT_DIR/prod_env_info.txt"
    
    echo "Production Environment Information" > "$info_file"
    echo "Generated: $(date)" >> "$info_file"
    echo "=================================" >> "$info_file"
    echo "" >> "$info_file"
    
    # Get system info
    echo "System Information:" >> "$info_file"
    ssh -i "$SSH_KEY" "$SSH_USER@$PROD_SERVER" "
        echo 'OS: ' \$(uname -a)
        echo 'Disk Usage: ' \$(df -h /)
        echo 'Memory: ' \$(free -h)
        echo 'Docker Version: ' \$(docker --version 2>/dev/null || echo 'Docker not installed')
        echo 'Docker Compose Version: ' \$(docker-compose --version 2>/dev/null || echo 'Docker Compose not installed')
    " >> "$info_file" 2>/dev/null
    
    echo "" >> "$info_file"
    
    # Get running containers
    echo "Running Containers:" >> "$info_file"
    ssh -i "$SSH_KEY" "$SSH_USER@$PROD_SERVER" "
        cd $PROD_PROJECT_DIR && docker-compose ps 2>/dev/null || echo 'No docker-compose running'
    " >> "$info_file" 2>/dev/null
    
    echo "" >> "$info_file"
    
    # Get environment files info
    echo "Environment Files:" >> "$info_file"
    ssh -i "$SSH_KEY" "$SSH_USER@$PROD_SERVER" "
        find $PROD_PROJECT_DIR -name '*.env*' -o -name '.env*' -exec ls -la {} \;
    " >> "$info_file" 2>/dev/null
}

# Main comparison function
main() {
    log_info "Starting Production vs Development Config/Env Files Comparison..."
    log_info "Task 087: Direct SSH-based comparison"
    
    # Test SSH connection first
    if ! test_ssh_connection; then
        log_error "Cannot proceed without SSH connection"
        exit 1
    fi
    
    # Initialize output files
    echo "Production vs Development Config/Env Files Comparison Report" > "$OUTPUT_DIR/summary.txt"
    echo "Generated: $(date)" >> "$OUTPUT_DIR/summary.txt"
    echo "=========================================================" >> "$OUTPUT_DIR/summary.txt"
    echo "" >> "$OUTPUT_DIR/summary.txt"
    
    echo "Detailed Configuration Analysis" > "$OUTPUT_DIR/detailed_analysis.txt"
    echo "Generated: $(date)" >> "$OUTPUT_DIR/detailed_analysis.txt"
    echo "==============================" >> "$OUTPUT_DIR/detailed_analysis.txt"
    echo "" >> "$OUTPUT_DIR/detailed_analysis.txt"
    
    # Get production environment info
    get_prod_env_info
    
    # Discover production files
    discover_prod_files
    
    # Compare main environment files
    log_step "Comparing main environment files..."
    
    # Development vs Production env files
    if [ -f "$LOCAL_PROJECT_DIR/config/development.env" ]; then
        if check_prod_file "$PROD_PROJECT_DIR/config/production.env"; then
            compare_env_files \
                "$LOCAL_PROJECT_DIR/config/development.env" \
                "$PROD_PROJECT_DIR/config/production.env" \
                "dev_vs_prod_env"
        else
            log_warning "Production env file not found: $PROD_PROJECT_DIR/config/production.env"
        fi
    else
        log_warning "Local development env file not found: $LOCAL_PROJECT_DIR/config/development.env"
    fi
    
    # Local production template vs actual production
    if [ -f "$LOCAL_PROJECT_DIR/config/production.env" ]; then
        if check_prod_file "$PROD_PROJECT_DIR/config/production.env"; then
            compare_env_files \
                "$LOCAL_PROJECT_DIR/config/production.env" \
                "$PROD_PROJECT_DIR/config/production.env" \
                "local_prod_template_vs_actual_prod"
        fi
    fi
    
    # Docker environment files
    if [ -f "$LOCAL_PROJECT_DIR/docker/env.prod.example" ]; then
        if check_prod_file "$PROD_PROJECT_DIR/docker/.env.prod"; then
            compare_env_files \
                "$LOCAL_PROJECT_DIR/docker/env.prod.example" \
                "$PROD_PROJECT_DIR/docker/.env.prod" \
                "docker_env_template_vs_prod"
        else
            log_warning "Production docker env file not found: $PROD_PROJECT_DIR/docker/.env.prod"
        fi
    fi
    
    # Check for staging environment
    if [ -f "$LOCAL_PROJECT_DIR/docker/env.stage.example" ]; then
        if check_prod_file "$PROD_PROJECT_DIR/docker/.env.stage"; then
            compare_env_files \
                "$LOCAL_PROJECT_DIR/docker/env.stage.example" \
                "$PROD_PROJECT_DIR/docker/.env.stage" \
                "docker_env_stage_template_vs_prod"
        else
            log_info "Production staging env file not found (this is normal if not using staging)"
        fi
    fi
    
    # Generate summary report
    log_step "Generating summary report..."
    
    echo "" >> "$OUTPUT_DIR/summary.txt"
    echo "Files analyzed:" >> "$OUTPUT_DIR/summary.txt"
    echo "- Local development: $LOCAL_PROJECT_DIR/config/development.env" >> "$OUTPUT_DIR/summary.txt"
    echo "- Local production template: $LOCAL_PROJECT_DIR/config/production.env" >> "$OUTPUT_DIR/summary.txt"
    echo "- Production actual: $PROD_PROJECT_DIR/config/production.env" >> "$OUTPUT_DIR/summary.txt"
    echo "- Docker environment files" >> "$OUTPUT_DIR/summary.txt"
    echo "" >> "$OUTPUT_DIR/summary.txt"
    echo "Detailed analysis available in: detailed_analysis.txt" >> "$OUTPUT_DIR/summary.txt"
    echo "Missing variables analysis available in: *_missing_variables.txt files" >> "$OUTPUT_DIR/summary.txt"
    echo "Production environment info available in: prod_env_info.txt" >> "$OUTPUT_DIR/summary.txt"
    
    log_success "Configuration comparison completed!"
    log_info "Results saved to: $OUTPUT_DIR/"
    log_info "Summary: $OUTPUT_DIR/summary.txt"
    log_info "Detailed analysis: $OUTPUT_DIR/detailed_analysis.txt"
    log_info "Production info: $OUTPUT_DIR/prod_env_info.txt"
    
    # Display summary
    echo ""
    echo "=== COMPARISON SUMMARY ==="
    cat "$OUTPUT_DIR/summary.txt"
    
    # Show missing variables files
    echo ""
    echo "=== MISSING VARIABLES ANALYSIS ==="
    find "$OUTPUT_DIR" -name "*_missing_variables.txt" | while read -r file; do
        echo "📄 $(basename "$file"):"
        head -10 "$file"
        echo ""
    done
}

# Run main function
main "$@"
