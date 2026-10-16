namespace Starter.Models
{
    public class SiteData
    {
        public string Brand { get; set; } = string.Empty;
        public string Tagline { get; set; } = string.Empty;
        public List<Category> Categories { get; set; } = new List<Category>();
        public List<Item> Items { get; set; } = new List<Item>();
        public List<Faq> Faqs { get; set; } = new List<Faq>();
    }

    public class Category
    {
        public string Key { get; set; } = string.Empty;
        public string Label { get; set; } = string.Empty;
    }

    public class Item
    {
        public string Key { get; set; } = string.Empty;
        public string Title { get; set; } = string.Empty;
        public string Category { get; set; } = string.Empty;
        public decimal Price { get; set; }
        public string Size { get; set; } = string.Empty;
        public string Image { get; set; } = string.Empty;
        public bool IsNew { get; set; }
        public string Text { get; set; } = string.Empty;
    }

    public class Subscriber
    {
        public string Email { get; set; } = string.Empty;
        public string From { get; set; } = string.Empty;
        public DateTime When { get; set; }
    }

    public class ContactMessage
    {
        public string Name { get; set; } = string.Empty;
        public string Email { get; set; } = string.Empty;
        public string Topic { get; set; } = string.Empty;
        public string Text { get; set; } = string.Empty;
        public DateTime When { get; set; }
    }

    public class Faq
    {
        public string Q { get; set; } = string.Empty;
        public string A { get; set; } = string.Empty;
    }
}
