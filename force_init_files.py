"""
Script to run 'pylockware init' in all subdirectories
"""
import subprocess
from pathlib import Path


def run_pylockware_init_all(root_dir: Path):
    """
    Run 'pylockware init' in all subdirectories
    
    Args:
        root_dir: Root directory containing subdirectories
    """
    print(f"Running 'pylockware init' in all subdirectories of: {root_dir}")
    print("=" * 60)
    
    # Get all subdirectories
    subdirs = [d for d in root_dir.iterdir() if d.is_dir() and not d.name.startswith('.')]
    
    for subdir in subdirs:
        print(f"\n[{subdir.name}]")
        print(f"  Running: pylockware init")
        
        try:
            result = subprocess.run(
                ['pylockware', 'init', "--force"],
                cwd=subdir,
                text=True,
                encoding='utf-8',
                errors='replace',
                timeout=30
            )
            
            if result.returncode == 0:
                print(f"  [OK] Success")
            else:
                print(f"  [FAIL] Failed (exit code: {result.returncode})")
            
            if result.stdout:
                print(f"  {result.stdout.strip()}")
            if result.stderr:
                print(f"  Error: {result.stderr.strip()}")
                
        except Exception as e:
            print(f"  [ERROR] {e}")
    
    print("\n" + "=" * 60)
    print(f"Processed {len(subdirs)} directories")


def main():
    """Main entry point"""
    import sys
    
    # Get path from command line or use 'examples' as default
    if len(sys.argv) > 1:
        path = sys.argv[1]
    else:
        path = "examples"
    
    root_dir = Path(path)
    if not root_dir.is_absolute():
        root_dir = Path.cwd() / root_dir
    
    if not root_dir.exists():
        print(f"Error: Directory does not exist: {root_dir}")
        return 1
    
    if not root_dir.is_dir():
        print(f"Error: Path is not a directory: {root_dir}")
        return 1
    
    run_pylockware_init_all(root_dir)
    return 0


if __name__ == "__main__":
    exit(main())
