using Microsoft.EntityFrameworkCore;
using System.Collections.Generic;
using System.Reflection.Emit;

namespace AIwebsite.Data
{
    public class AiWebsiteDbContext : DbContext
    {
        public AiWebsiteDbContext(DbContextOptions<AiWebsiteDbContext> options) : base(options)
        {
        }

        protected override void OnModelCreating(ModelBuilder modelBuilder)
        {
            base.OnModelCreating(modelBuilder);
        }

        public DbSet<Entities.t00Conversation> t00Conversation { get; set; }
        public DbSet<Entities.t00ConversationHistory> t00ConversationHistory { get; set; }
        public DbSet<Entities.t00ContactUs> t00ContactUs { get; set; }

    }
}
