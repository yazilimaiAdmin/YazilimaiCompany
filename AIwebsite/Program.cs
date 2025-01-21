using AIwebsite.Data;
using Microsoft.AspNetCore.Components;
using Microsoft.AspNetCore.Components.Web;
using Syncfusion.Blazor;
using System.Globalization;
using AIwebsite.Shared;
using Microsoft.Extensions.Options;
using Microsoft.AspNetCore.Localization;
using AIwebsite.Services;
using Microsoft.EntityFrameworkCore;

var builder = WebApplication.CreateBuilder(args);

builder.Services.AddLocalization(options => options.ResourcesPath = "Resources");

builder.Services.AddSignalR(hubOptions =>
{
    hubOptions.ClientTimeoutInterval = TimeSpan.FromHours(2); // Set timeout to 2 hours
});

builder.Services.AddDbContextPool<ApplicationDbContext>(options =>
options.UseSqlServer(builder.Configuration.GetConnectionString("AiWebsiteConnection")));

// Add services to the container.

var cultureInfo = new CultureInfo("tr");
CultureInfo.DefaultThreadCurrentCulture = cultureInfo;
CultureInfo.DefaultThreadCurrentUICulture = cultureInfo;



var supportedCultures = new[] { "tr", "en-US" };
var localizationOptions = new RequestLocalizationOptions()
    .SetDefaultCulture(supportedCultures[1]) // This sets Turkish as the default language
    .AddSupportedCultures(supportedCultures)
    .AddSupportedUICultures(supportedCultures);

CultureInfo.DefaultThreadCurrentCulture = new CultureInfo(supportedCultures[1]);
CultureInfo.DefaultThreadCurrentUICulture = new CultureInfo(supportedCultures[1]);

var syncfusionLicenseKey = builder.Configuration["Syncfusion:LicenseKey"];
Syncfusion.Licensing.SyncfusionLicenseProvider.RegisterLicense(syncfusionLicenseKey);



// Register Syncfusion services
builder.Services.AddSyncfusionBlazor();

builder.Services.AddRazorPages();
builder.Services.AddServerSideBlazor();
builder.Services.AddSingleton<WeatherForecastService>();
builder.Services.AddScoped<ChatService>();


var app = builder.Build();

// Configure the HTTP request pipeline.
app.UseRequestLocalization(localizationOptions);




if (!app.Environment.IsDevelopment())
{
    app.UseExceptionHandler("/Error");
    // The default HSTS value is 30 days. You may want to change this for production scenarios, see https://aka.ms/aspnetcore-hsts.
    app.UseHsts();
}

app.UseHttpsRedirection();




app.UseStaticFiles();

app.UseRouting();

app.MapControllers();
app.MapBlazorHub();
app.MapFallbackToPage("/_Host");

app.Run();
