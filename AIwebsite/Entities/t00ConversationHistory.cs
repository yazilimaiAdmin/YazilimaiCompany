using System.ComponentModel.DataAnnotations;

namespace AIwebsite.Entities
{
    public class t00ConversationHistory
    {
        [Key]
        public int ID { get; set; }
        public int ConversationId { get; set; }
        public int UserTypeId { get; set; }
        public string Message { get; set; }
        public DateTime Date { get; set; }
    }
}
