#!/usr/bin/env python3
"""
Main entry point for the User Details Research Crew.

This script allows you to run the User Details Crew standalone to research
professional information about individuals using their email and name.

Usage:
    python main.py --email "user@example.com" --name "John Doe"
    python main.py --email "user@example.com" --name "John Doe" --force-refresh
    python main.py --email "user@example.com"  # name is optional

Example:
    python main.py --email "marco@vapi.ai" --name "Marco Bariani"
"""

import sys
import os
import argparse
import json
from pathlib import Path
from dotenv import load_dotenv

# Add the project root to Python path
project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# Load environment variables from .env file
env_path = project_root / ".env"
if env_path.exists():
    load_dotenv(env_path)
else:
    print(f"Warning: .env file not found at {env_path}")
    print("Please ensure OPENAI_API_KEY and EXA_API_KEY are set in environment variables")

# Check required environment variables
required_vars = ["OPENAI_API_KEY", "EXA_API_KEY"]
missing_vars = [var for var in required_vars if not os.getenv(var)]
if missing_vars:
    print(f"Error: Missing required environment variables: {', '.join(missing_vars)}")
    print("Please set these variables in your .env file or environment")
    sys.exit(1)

from user_details_crew import UserDetailsCrew
from email_auto_responder_flow.models import UserDetails
from email_auto_responder_flow.utils.user_storage import UserStorage


def process_single_email(crew: UserDetailsCrew, args):
    """Process a single email address."""
    print(f"🔍 Researching user details for: {args.email}")
    if args.name:
        print(f"📝 Name: {args.name}")
    if args.force_refresh:
        print("🔄 Force refresh enabled")
    print("\n" + "="*50)
    
    # Fetch user details
    user_details = crew.fetch_user_details(
        email=args.email,
        name=args.name,
        force_refresh=args.force_refresh
    )
    
    # Output results based on format
    if args.output_format == "json":
        print(json.dumps(user_details.__dict__, indent=2, default=str))
    elif args.output_format == "summary":
        print_summary(user_details)
    else:  # pretty format
        print_pretty_output(user_details)


def process_user_list(crew: UserDetailsCrew, args):
    """Process all users from the stored user list."""
    print("🔍 Processing users from stored user list...")
    if args.force_refresh:
        print("🔄 Force refresh enabled for all users")
    print(f"📦 Batch size: {args.batch_size}")
    print("\n" + "="*50)
    
    # Initialize user storage
    user_storage = UserStorage()
    
    # Get all users from storage
    all_users = user_storage.get_all_users()
    
    if not all_users:
        print("❌ No users found in storage")
        print("💡 Tip: Users are automatically added when emails are processed")
        return
    
    print(f"📊 Found {len(all_users)} users in storage")
    
    # Process users in batches
    processed_count = 0
    failed_count = 0
    
    for i in range(0, len(all_users), args.batch_size):
        batch = all_users[i:i + args.batch_size]
        batch_num = (i // args.batch_size) + 1
        total_batches = (len(all_users) + args.batch_size - 1) // args.batch_size
        
        print(f"\n🔄 Processing batch {batch_num}/{total_batches} ({len(batch)} users)")
        print("-" * 40)
        
        for user in batch:
            try:
                print(f"\n👤 Processing: {user.email}")
                if user.name:
                    print(f"   Name: {user.name}")
                
                # Fetch updated user details
                updated_user = crew.fetch_user_details(
                    email=user.email,
                    name=user.name,
                    force_refresh=args.force_refresh
                )
                
                # Output based on format
                if args.output_format == "json":
                    print(json.dumps(updated_user.__dict__, indent=2, default=str))
                elif args.output_format == "summary":
                    print_user_summary_inline(updated_user)
                else:  # pretty format
                    print_user_pretty_inline(updated_user)
                
                processed_count += 1
                print("   ✅ Success")
                
            except Exception as e:
                failed_count += 1
                print(f"   ❌ Failed: {str(e)}")
                if args.verbose:
                    import traceback
                    traceback.print_exc()
        
        # Show progress
        remaining = len(all_users) - (i + len(batch))
        if remaining > 0:
            print(f"\n⏳ {remaining} users remaining...")
    
    # Final summary
    print("\n" + "="*60)
    print("📋 BATCH PROCESSING COMPLETE")
    print(f"✅ Successfully processed: {processed_count} users")
    if failed_count > 0:
        print(f"❌ Failed: {failed_count} users")
    print(f"📊 Total users: {len(all_users)}")
    print("="*60)


def print_user_summary_inline(user_details: UserDetails):
    """Print a brief inline summary for batch processing."""
    print(f"   📧 {user_details.email}")
    print(f"   🏢 {user_details.company or 'N/A'} | 💼 {user_details.role or 'N/A'}")
    social_count = sum(1 for url in [user_details.linkedin_url, user_details.twitter_url, user_details.website] if url)
    print(f"   🔗 {social_count} social links | 📍 {user_details.location or 'N/A'}")


def print_user_pretty_inline(user_details: UserDetails):
    """Print a condensed pretty format for batch processing."""
    print(f"   📧 Email: {user_details.email}")
    print(f"   👤 Name: {user_details.name or 'Not available'}")
    print(f"   🏢 Company: {user_details.company or 'Not available'}")
    print(f"   💼 Role: {user_details.role or 'Not available'}")
    print(f"   📍 Location: {user_details.location or 'Not available'}")
    if user_details.bio:
        bio_preview = user_details.bio[:100] + "..." if len(user_details.bio) > 100 else user_details.bio
        print(f"   📝 Bio: {bio_preview}")
    social_links = []
    if user_details.linkedin_url:
        social_links.append("LinkedIn")
    if user_details.twitter_url:
        social_links.append("Twitter")
    if user_details.website:
        social_links.append("Website")
    print(f"   🔗 Social: {', '.join(social_links) if social_links else 'None'}")


def main():
    """Main function to run the User Details Research Crew."""
    parser = argparse.ArgumentParser(
        description="Research professional information about a user",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Single email processing
  python main.py --email "marco@vapi.ai" --name "Marco Bariani"
  python main.py --email "john@company.com" --name "John Smith" --force-refresh
  python main.py --email "user@example.com"  # name is optional
  
  # Batch processing from user list
  python main.py --from-user-list
  python main.py --from-user-list --batch-size 5
  python main.py --from-user-list --force-refresh --output-format summary
  python main.py --from-user-list --batch-size 20 --output-format json
        """
    )
    
    parser.add_argument(
        "--email",
        help="Email address of the person to research"
    )
    
    parser.add_argument(
        "--from-user-list",
        action="store_true",
        help="Process all emails from the stored user list"
    )
    
    parser.add_argument(
        "--batch-size",
        type=int,
        default=10,
        help="Number of users to process in batch mode (default: 10)"
    )
    
    parser.add_argument(
        "--name",
        help="Name of the person to research (optional but recommended)"
    )
    
    parser.add_argument(
        "--force-refresh",
        action="store_true",
        help="Force refresh even if user details already exist"
    )
    
    parser.add_argument(
        "--output-format",
        choices=["json", "pretty", "summary"],
        default="pretty",
        help="Output format (default: pretty)"
    )
    
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose output"
    )
    
    args = parser.parse_args()
    
    # Validate arguments
    if not args.email and not args.from_user_list:
        print("Error: Either --email or --from-user-list must be specified")
        parser.print_help()
        sys.exit(1)
    
    if args.email and args.from_user_list:
        print("Error: Cannot use both --email and --from-user-list at the same time")
        sys.exit(1)
    
    if args.email and "@" not in args.email:
        print("Error: Invalid email format")
        sys.exit(1)
    
    try:
        # Initialize the crew
        crew = UserDetailsCrew()
        
        if args.from_user_list:
            # Process all users from the user list
            process_user_list(crew, args)
        else:
            # Process single email
            process_single_email(crew, args)
            
    except KeyboardInterrupt:
        print("\n\n⚠️  Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


def print_pretty_output(user_details: UserDetails):
    """Print user details in a pretty, human-readable format."""
    print("\n✅ User Details Research Complete!\n")
    print("="*60)
    print(f"📧 Email: {user_details.email}")
    print(f"👤 Name: {user_details.name or 'Not available'}")
    print(f"🏢 Company: {user_details.company or 'Not available'}")
    print(f"💼 Role: {user_details.role or 'Not available'}")
    print(f"📍 Location: {user_details.location or 'Not available'}")
    print(f"🏭 Industry: {user_details.industry or 'Not available'}")
    print("="*60)
    
    if user_details.bio:
        print(f"\n📝 Bio:\n{user_details.bio}")
    
    print("\n🔗 Social Links:")
    if user_details.linkedin_url:
        print(f"   LinkedIn: {user_details.linkedin_url}")
    if user_details.twitter_url:
        print(f"   Twitter: {user_details.twitter_url}")
    if user_details.website:
        print(f"   Website: {user_details.website}")
    
    if not any([user_details.linkedin_url, user_details.twitter_url, user_details.website]):
        print("   No social links found")
    
    print(f"\n📊 Metadata:")
    print(f"   Source: {user_details.source}")
    print(f"   Created: {user_details.created_at}")
    print(f"   Updated: {user_details.updated_at}")
    print("\n" + "="*60)


def print_summary(user_details: UserDetails):
    """Print a brief summary of user details."""
    print(f"\n📋 Summary for {user_details.email}:")
    print(f"   Name: {user_details.name or 'N/A'}")
    print(f"   Company: {user_details.company or 'N/A'}")
    print(f"   Role: {user_details.role or 'N/A'}")
    print(f"   Location: {user_details.location or 'N/A'}")
    
    social_count = sum(1 for url in [user_details.linkedin_url, user_details.twitter_url, user_details.website] if url)
    print(f"   Social Links: {social_count} found")
    print(f"   Source: {user_details.source}")


if __name__ == "__main__":
    main()