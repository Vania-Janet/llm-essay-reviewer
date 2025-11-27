"""
Migration script to move files from old structure to new organized structure.

This script helps migrate from the flat structure to the new modular structure.
Run this after setting up the new directory structure.
"""
import shutil
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).parent.parent
OLD_WEB = BASE_DIR / "web"
NEW_STRUCTURE = BASE_DIR / "essay_evaluator"

def migrate_files():
    """Migrate files to new structure."""
    
    print("🚀 Starting migration to new project structure...")
    print("=" * 60)
    
    migrations = [
        # Core files
        ("agent.py", "essay_evaluator/core/agent/evaluator.py"),
        ("models.py", "essay_evaluator/core/models/evaluation.py"),
        ("prompts.py", "essay_evaluator/core/evaluation/prompts.py"),
        
        # Utility files
        ("pdf_processor.py", "essay_evaluator/utils/pdf/processor.py"),
        ("database.py", "essay_evaluator/utils/database/connection.py"),
        
        # API files
        ("web/app.py", "essay_evaluator/api/app.py"),
        ("web/auth.py", "essay_evaluator/api/routes/auth.py"),
        
        # Web static files
        ("web/styles.css", "essay_evaluator/web/static/css/styles.css"),
        ("web/script.js", "essay_evaluator/web/static/js/script.js"),
        ("web/criteria-management.js", "essay_evaluator/web/static/js/criteria-management.js"),
        
        # Web templates
        ("web/index.html", "essay_evaluator/web/templates/index.html"),
        ("web/login.html", "essay_evaluator/web/templates/login.html"),
        
        # Web images
        ("web/icon.png", "essay_evaluator/web/static/images/icon.png"),
        ("web/image.png", "essay_evaluator/web/static/images/logo.png"),
        
        # Scripts
        ("load_processed_essays.py", "scripts/load_processed_essays.py"),
        ("check_database.py", "scripts/check_database.py"),
        ("evaluar_pdfs.py", "scripts/batch_evaluate.py"),
        
        # Tests
        ("test_agent.py", "essay_evaluator/tests/test_agent.py"),
        
        # Data
        ("essays.db", "essay_evaluator/data/database/essays.db"),
    ]
    
    success_count = 0
    skip_count = 0
    error_count = 0
    
    for old_path, new_path in migrations:
        old_file = BASE_DIR / old_path
        new_file = BASE_DIR / new_path
        
        if not old_file.exists():
            print(f"⏭️  Skip: {old_path} (not found)")
            skip_count += 1
            continue
        
        if new_file.exists():
            print(f"⏭️  Skip: {new_path} (already exists)")
            skip_count += 1
            continue
        
        try:
            # Create parent directory if needed
            new_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Copy file
            shutil.copy2(old_file, new_file)
            print(f"✅ Migrated: {old_path} → {new_path}")
            success_count += 1
            
        except Exception as e:
            print(f"❌ Error migrating {old_path}: {e}")
            error_count += 1
    
    print("=" * 60)
    print(f"\n📊 Migration Summary:")
    print(f"   ✅ Successful: {success_count}")
    print(f"   ⏭️  Skipped: {skip_count}")
    print(f"   ❌ Errors: {error_count}")
    
    if error_count == 0:
        print("\n🎉 Migration completed successfully!")
        print("\n📝 Next steps:")
        print("   1. Update import statements in migrated files")
        print("   2. Test the application: python -m essay_evaluator.api.app")
        print("   3. Run tests: pytest")
        print("   4. Update documentation if needed")
    else:
        print("\n⚠️  Migration completed with errors. Please review and fix manually.")
    
    return error_count == 0


def create_directory_structure():
    """Create the new directory structure."""
    
    print("\n📁 Creating directory structure...")
    
    directories = [
        "essay_evaluator/core/agent",
        "essay_evaluator/core/evaluation",
        "essay_evaluator/core/models",
        "essay_evaluator/api/routes",
        "essay_evaluator/api/middleware",
        "essay_evaluator/web/static/css",
        "essay_evaluator/web/static/js",
        "essay_evaluator/web/static/images",
        "essay_evaluator/web/templates",
        "essay_evaluator/utils/pdf",
        "essay_evaluator/utils/database",
        "essay_evaluator/data/raw",
        "essay_evaluator/data/processed",
        "essay_evaluator/data/database",
        "essay_evaluator/tests/fixtures",
        "scripts",
        "docs/architecture",
        "docs/api",
        "docs/user_guide",
        "config",
        "logs",
    ]
    
    for directory in directories:
        dir_path = BASE_DIR / directory
        dir_path.mkdir(parents=True, exist_ok=True)
        
        # Create __init__.py in Python packages
        if directory.startswith("essay_evaluator"):
            init_file = dir_path / "__init__.py"
            if not init_file.exists():
                init_file.touch()
    
    print("✅ Directory structure created")


def main():
    """Main migration function."""
    
    print("\n" + "=" * 60)
    print("📦 Essay Evaluator - Project Structure Migration")
    print("=" * 60 + "\n")
    
    response = input("This will reorganize your project structure. Continue? (y/n): ")
    if response.lower() != 'y':
        print("Migration cancelled.")
        return
    
    # Step 1: Create directory structure
    create_directory_structure()
    
    # Step 2: Migrate files
    success = migrate_files()
    
    if success:
        print("\n✨ All done! Your project is now professionally organized.")
        print("\n📚 Documentation generated:")
        print("   - README_NEW.md (comprehensive README)")
        print("   - docs/architecture/system_design.md")
        print("   - docs/user_guide/getting_started.md")
        print("\n🔧 Configuration files created:")
        print("   - config/development.py")
        print("   - config/production.py")
        print("   - .env.example")
        print("   - setup.py")


if __name__ == "__main__":
    main()
