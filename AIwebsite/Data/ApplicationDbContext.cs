using Microsoft.EntityFrameworkCore;

namespace AIwebsite.Data
{
    public class ApplicationDbContext : DbContext
    {
        public ApplicationDbContext(DbContextOptions<ApplicationDbContext> options)
            : base(options)
        {
        }

        public DbSet<ChatMessageEntity> ChatMessages { get; set; }
    }
}
