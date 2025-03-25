"""
In-memory database to store user referrals and track invitations.
"""

class Database:
    def __init__(self):
        # Dictionary to store user referrals
        # Format: {user_id: {referrer_id: user_id_who_referred, invited: [user_ids_invited]}}
        self.users = {}
        
    def add_user(self, user_id, referrer_id=None):
        """
        Add a user to the database.
        
        Args:
            user_id: Telegram user ID
            referrer_id: ID of the user who referred this user (if any)
        
        Returns:
            Boolean indicating if the user was newly added
        """
        # If the user already exists, just return False
        if user_id in self.users:
            return False
            
        # Add the user
        self.users[user_id] = {
            "referrer_id": referrer_id,
            "invited": []
        }
        
        # If the user was referred by someone, update the referrer's invited list
        if referrer_id and referrer_id in self.users:
            # Only add if not already in the list
            if user_id not in self.users[referrer_id]["invited"]:
                self.users[referrer_id]["invited"].append(user_id)
        
        return True
    
    def get_invites_count(self, user_id):
        """
        Get the number of people a user has invited.
        
        Args:
            user_id: Telegram user ID
            
        Returns:
            Number of invites
        """
        if user_id not in self.users:
            return 0
        
        return len(self.users[user_id]["invited"])
    
    def get_referrer(self, user_id):
        """
        Get the ID of the user who referred this user.
        
        Args:
            user_id: Telegram user ID
            
        Returns:
            Referrer user ID or None
        """
        if user_id not in self.users:
            return None
        
        return self.users[user_id]["referrer_id"]

# Create a single instance of the database to be used throughout the application
db = Database()
