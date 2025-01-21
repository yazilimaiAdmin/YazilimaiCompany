using System.ComponentModel.DataAnnotations;

namespace AIwebsite.Data // Or your preferred namespace
{
    public class ChatMessageEntity
    {
        [Key]
        public int Id { get; set; }
        public int ConversationId { get; set; } // Unique ID for each conversation
        public string UserId { get; set; } // Optional user ID
        public string Content { get; set; }
        public string Role { get; set; } // User or Assistant
        public DateTime Timestamp { get; set; }
    }
}
