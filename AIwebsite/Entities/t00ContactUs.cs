using System.ComponentModel.DataAnnotations;

namespace AIwebsite.Entities
{
    public class t00ContactUs
    {
        [Key]
        public int ID { get; set; }
        public string Name { get; set; }
        public string Email { get; set; }
        public string Phonenumber { get; set; }
        public string Message { get; set; }
        public DateTime Date { get; set; }
    }
}
