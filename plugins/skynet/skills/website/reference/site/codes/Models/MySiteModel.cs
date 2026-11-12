namespace MySite.Models
{
    public class SiteData
    {
        public string Brand { get; set; } = string.Empty;
        public string Tagline { get; set; } = string.Empty;
        public string Phone { get; set; } = string.Empty;
        public string Email { get; set; } = string.Empty;
        public string Address { get; set; } = string.Empty;
        public string Hours { get; set; } = string.Empty;
        public List<Category> Categories { get; set; } = new List<Category>();
        public List<Item> Items { get; set; } = new List<Item>();
        public List<Faq> Faqs { get; set; } = new List<Faq>();
        public int MaxVideoMb { get; set; } = 30;
        public Dictionary<string, PageDoc> Pages { get; set; } = new Dictionary<string, PageDoc>();
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

    public class ContactMessage
    {
        public string Id { get; set; } = string.Empty;
        public string Name { get; set; } = string.Empty;
        public string Email { get; set; } = string.Empty;
        public string Phone { get; set; } = string.Empty;
        public string Topic { get; set; } = string.Empty;
        public string Text { get; set; } = string.Empty;
        public DateTime When { get; set; }
        public bool Read { get; set; }
        public string Status { get; set; } = "new";
        public string Note { get; set; } = string.Empty;
        public DateTime Changed { get; set; }
    }

    public class Faq
    {
        public string Q { get; set; } = string.Empty;
        public string A { get; set; } = string.Empty;
    }
    public class MediaItem
    {
        public string Id { get; set; } = string.Empty;
        public string Path { get; set; } = string.Empty;
        public string Thumb { get; set; } = string.Empty;
        public string Kind { get; set; } = "photo";
        public string Name { get; set; } = string.Empty;
        public string Alt { get; set; } = string.Empty;
        public string Caption { get; set; } = string.Empty;
        public long Bytes { get; set; }
        public DateTime Added { get; set; }
        public string By { get; set; } = string.Empty;
    }

    public class PageDoc
    {
        public List<Block> Blocks { get; set; } = new List<Block>();
        public List<PageVersion> Versions { get; set; } = new List<PageVersion>();
        public DateTime Saved { get; set; }
        public string By { get; set; } = string.Empty;
    }

    public class Block
    {
        public string Id { get; set; } = string.Empty;
        public string Type { get; set; } = string.Empty;
        public string Source { get; set; } = string.Empty;
        public bool Hidden { get; set; }
        public string Kicker { get; set; } = string.Empty;
        public string Title { get; set; } = string.Empty;
        public string Text { get; set; } = string.Empty;
        public string Media { get; set; } = string.Empty;
        public string Label { get; set; } = string.Empty;
        public string Link { get; set; } = string.Empty;
        public string Label2 { get; set; } = string.Empty;
        public string Link2 { get; set; } = string.Empty;
        public bool Flip { get; set; }
        public List<BlockItem> Items { get; set; } = new List<BlockItem>();
    }

    public class BlockItem
    {
        public string Icon { get; set; } = string.Empty;
        public string Media { get; set; } = string.Empty;
        public string Title { get; set; } = string.Empty;
        public string Text { get; set; } = string.Empty;
        public string Link { get; set; } = string.Empty;
        public string Label { get; set; } = string.Empty;
    }

    public class PageVersion
    {
        public DateTime When { get; set; }
        public string By { get; set; } = string.Empty;
        public List<Block> Blocks { get; set; } = new List<Block>();
    }

    public class Staff
    {
        public string Id { get; set; } = string.Empty;
        public string Login { get; set; } = string.Empty;
        public string Name { get; set; } = string.Empty;
        public string Title { get; set; } = string.Empty;
        public string Hash { get; set; } = string.Empty;
        public bool Admin { get; set; }
        public bool Active { get; set; } = true;
        public bool MustChange { get; set; }
        public Dictionary<string, string> Perms { get; set; } = new Dictionary<string, string>();
    }

    public class Session
    {
        public string Token { get; set; } = string.Empty;
        public string User { get; set; } = string.Empty;
        public DateTime Expires { get; set; }
    }

    public class ActivityEntry
    {
        public DateTime When { get; set; }
        public string User { get; set; } = string.Empty;
        public string Action { get; set; } = string.Empty;
        public string Target { get; set; } = string.Empty;
        public bool Ok { get; set; } = true;
    }

    public class FloorPlan
    {
        public List<PlanFloor> Floors { get; set; } = new List<PlanFloor>();
    }

    public class PlanFloor
    {
        public string Name { get; set; } = string.Empty;
        public List<PlanRoom> Rooms { get; set; } = new List<PlanRoom>();
        public List<PlanOpening> Openings { get; set; } = new List<PlanOpening>();
    }

    public class PlanRoom
    {
        public string Name { get; set; } = string.Empty;
        public string Kind { get; set; } = "living";
        public int X { get; set; }
        public int Y { get; set; }
        public int W { get; set; }
        public int H { get; set; }
    }

    public class PlanOpening
    {
        public string Kind { get; set; } = "door";
        public int X { get; set; }
        public int Y { get; set; }
        public int Len { get; set; }
        public string Dir { get; set; } = "h";
    }

    public class Thing
    {
        public string Id { get; set; } = string.Empty;
        public string Name { get; set; } = string.Empty;
        public List<string> Photos { get; set; } = new List<string>();
        public FloorPlan Plan { get; set; } = new FloorPlan();
    }
}
