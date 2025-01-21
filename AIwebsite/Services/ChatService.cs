using Azure.AI.OpenAI;
using Azure.Identity;
using Azure.Security.KeyVault.Secrets;
using Azure;
using AIwebsite.Data;
using Microsoft.Extensions.Configuration;

namespace AIwebsite.Services
{
    public class ChatService
    {
        private OpenAIClient client;
        private readonly ApplicationDbContext _dbContext;

        public ChatService(ApplicationDbContext dbContext, IConfiguration configuration)
        {
            _dbContext = dbContext;

            // Securely fetch Key Vault URI and Secret Name from configuration settings
            var keyVaultUri = new Uri(configuration["KeyVault:Uri"]);
            var secretClient = new SecretClient(keyVaultUri, new DefaultAzureCredential());
            KeyVaultSecret secret = secretClient.GetSecret(configuration["KeyVault:SecretName"]);
            var apiKey = secret.Value;

            // Securely fetch OpenAI endpoint from configuration
            client = new OpenAIClient(
                new Uri(configuration["OpenAI:Endpoint"]),
                new AzureKeyCredential(apiKey)
            );
        }

        public async Task<ChatCompletions> GetChatCompletionsAsync(List<ChatMessage> messages)
        {
            ChatCompletionsOptions options = new ChatCompletionsOptions()
            {
                Temperature = 1f,
                MaxTokens = 400,
                NucleusSamplingFactor = 0.95f,
                FrequencyPenalty = 0,
                PresencePenalty = 0,
            };

            foreach (var message in messages)
            {
                options.Messages.Add(message);
            }

            Response<ChatCompletions> response = await client.GetChatCompletionsAsync(
                "gpt-4o",
                options
            );

            // Store the messages in the database
            await SaveChatMessagesToDatabase(messages);

            return response.Value;
        }

        public async Task<int> StartNewConversationAsync()
        {
            return GetConversationId();
        }

        public async Task SaveChatMessageToDatabaseAsync(int conversationId, ChatMessage message)
        {
            _dbContext.ChatMessages.Add(new ChatMessageEntity
            {
                ConversationId = conversationId,
                UserId = GetUserId(), // Placeholder for authentication
                Content = message.Content,
                Role = message.Role.ToString(),
                Timestamp = DateTime.UtcNow
            });

            await _dbContext.SaveChangesAsync();
        }

        private async Task SaveChatMessagesToDatabase(List<ChatMessage> messages)
        {
            int conversationId = GetConversationId();

            foreach (var message in messages)
            {
                if (message.Role != ChatRole.System)
                {
                    _dbContext.ChatMessages.Add(new ChatMessageEntity
                    {
                        ConversationId = conversationId,
                        UserId = GetUserId(),
                        Content = message.Content,
                        Role = message.Role.ToString(),
                        Timestamp = DateTime.UtcNow
                    });
                }
            }

            await _dbContext.SaveChangesAsync();
        }

        private int GetConversationId()
        {
            int lastConversationId = _dbContext.ChatMessages.Max(m => (int?)m.ConversationId) ?? 0;
            return lastConversationId + 1;
        }

        private string GetUserId()
        {
            return "1"; // Placeholder for now
        }

        private bool UserSpecifiedTechnologies(string userInput)
        {
            var technologies = new List<string> { "c#", ".net", "blazor", "azure", "sql server", "python", "machine learning", "data analysis" };
            return technologies.Any(tech => userInput.ToLower().Contains(tech));
        }

        private bool AiResponseMentionsTechnologies(string aiMessageContent)
        {
            var technologies = new List<string> { "c#", ".net", "blazor", "azure", "sql server", "python", "machine learning", "data analysis" };
            return technologies.Any(tech => aiMessageContent.ToLower().Contains(tech));
        }

        private bool AskingAboutTechnologies(string aiMessageContent)
        {
            return aiMessageContent.ToLower().Contains("technologies") || aiMessageContent.ToLower().Contains("methods") || aiMessageContent.ToLower().Contains("programming");
        }
    }
}
