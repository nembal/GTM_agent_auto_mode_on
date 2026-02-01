"""
github_stargazer_scraper

Identify and extract profile information about users who have starred specific
GitHub repositories, enabling targeted outreach to developers and technical leaders.

Built by Builder from PRD: github_stargazer_scraper
"""

import os
import time
from typing import Optional
import requests


def github_stargazer_scraper(
    repo_identifiers: list[str],
    min_followers: Optional[int] = None,
    has_company: Optional[bool] = None,
    has_email: Optional[bool] = None,
    limit: int = 100
) -> dict:
    """
    Scrape GitHub stargazers from specified repositories and extract their profiles.

    Args:
        repo_identifiers: List of repository paths (e.g., ['owner/repo', 'other/repo'])
        min_followers: Optional minimum follower count filter
        has_company: Optional filter requiring company field
        has_email: Optional filter requiring public email
        limit: Maximum number of users to return (default: 100)

    Returns:
        dict with:
            - result: Dict containing 'users' list and 'total_scanned' count
            - success: Boolean indicating success
            - error: Error message if any
    """
    result = {"users": [], "total_scanned": 0}

    try:
        # Get GitHub token from environment (optional but helps with rate limits)
        github_token = os.getenv("GITHUB_TOKEN")
        headers = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28"
        }
        if github_token:
            headers["Authorization"] = f"Bearer {github_token}"

        # Track unique users across repos
        seen_users = set()
        users_data = []

        # Iterate through each repository
        for repo_path in repo_identifiers:
            if len(users_data) >= limit:
                break

            # Parse owner/repo format
            parts = repo_path.split("/")
            if len(parts) != 2:
                continue
            owner, repo = parts

            # Fetch stargazers with pagination
            page = 1
            per_page = 100

            while len(users_data) < limit:
                # Get stargazers page
                stargazers_url = f"https://api.github.com/repos/{owner}/{repo}/stargazers"
                params = {"per_page": per_page, "page": page}

                stargazers_response = requests.get(
                    stargazers_url,
                    headers=headers,
                    params=params,
                    timeout=10
                )

                # Check rate limit
                if stargazers_response.status_code == 403:
                    # Hit rate limit, return partial results
                    return {
                        "result": {
                            "users": users_data,
                            "total_scanned": result["total_scanned"],
                            "rate_limited": True
                        },
                        "success": False,
                        "error": "GitHub API rate limit reached"
                    }

                if stargazers_response.status_code != 200:
                    # Non-fatal error, skip this repo
                    break

                stargazers = stargazers_response.json()

                # No more stargazers
                if not stargazers:
                    break

                # Fetch full profile for each stargazer
                for stargazer in stargazers:
                    if len(users_data) >= limit:
                        break

                    username = stargazer.get("login")
                    if not username or username in seen_users:
                        continue

                    result["total_scanned"] += 1

                    # Get full user profile
                    user_url = f"https://api.github.com/users/{username}"
                    user_response = requests.get(
                        user_url,
                        headers=headers,
                        timeout=10
                    )

                    if user_response.status_code == 403:
                        # Hit rate limit during user fetch
                        return {
                            "result": {
                                "users": users_data,
                                "total_scanned": result["total_scanned"],
                                "rate_limited": True
                            },
                            "success": False,
                            "error": "GitHub API rate limit reached during user fetch"
                        }

                    if user_response.status_code != 200:
                        continue

                    user_data = user_response.json()

                    # Apply filters
                    if min_followers is not None:
                        if user_data.get("followers", 0) < min_followers:
                            continue

                    if has_company is True:
                        if not user_data.get("company"):
                            continue

                    if has_email is True:
                        if not user_data.get("email"):
                            continue

                    # Build user record
                    user_record = {
                        "username": user_data.get("login"),
                        "display_name": user_data.get("name"),
                        "company": user_data.get("company"),
                        "bio": user_data.get("bio"),
                        "email": user_data.get("email"),
                        "location": user_data.get("location"),
                        "followers": user_data.get("followers", 0),
                        "profile_url": user_data.get("html_url"),
                        "starred_repos": [repo_path]
                    }

                    # Check if user already exists (starred multiple repos)
                    existing_user = next(
                        (u for u in users_data if u["username"] == username),
                        None
                    )

                    if existing_user:
                        # Add this repo to their starred_repos list
                        if repo_path not in existing_user["starred_repos"]:
                            existing_user["starred_repos"].append(repo_path)
                    else:
                        # New user
                        seen_users.add(username)
                        users_data.append(user_record)

                    # Rate limit protection: small delay between requests
                    time.sleep(0.1)

                # Move to next page
                page += 1

                # GitHub API max page limit safety check
                if page > 100:
                    break

        return {
            "result": {
                "users": users_data,
                "total_scanned": result["total_scanned"]
            },
            "success": True,
            "error": None
        }

    except requests.exceptions.RequestException as e:
        return {
            "result": result,
            "success": False,
            "error": f"Network error: {str(e)}"
        }

    except Exception as e:
        return {
            "result": result,
            "success": False,
            "error": str(e)
        }


# For Executor compatibility
run = github_stargazer_scraper
