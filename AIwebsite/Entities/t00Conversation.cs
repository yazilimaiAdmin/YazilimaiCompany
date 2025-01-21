using System.ComponentModel.DataAnnotations;

namespace AIwebsite.Entities
{
    public class t00Conversation
    {
        [Key]
        public int ID { get; set; }
        public DateTime Date { get; set; }
    }
}
