export type BlogPostMeta = {
  slug: string;
  title: string;
  date: string;
  featuredImage?: string;
};

export type BlogPost = BlogPostMeta & {
  content: string;
};

const rawPosts = import.meta.glob('../content/blog/*.md', {
  as: 'raw',
  eager: true,
}) as Record<string, string>;

function parseFrontMatter(markdown: string): {
  meta: Partial<BlogPostMeta>;
  body: string;
} {
  // Minimal front matter parser: expects first heading as title if no explicit front matter
  const lines = markdown.trimStart().split('\n');
  let title = '';
  let featuredImage = '';
  let i = 0;

  // Check for front matter
  if (lines[0].startsWith('---')) {
    i = 1;
    while (i < lines.length && !lines[i].startsWith('---')) {
      const line = lines[i];
      if (line.startsWith('title:')) {
        title = line.replace(/^title:\s*/, '').trim();
      } else if (line.startsWith('featuredImage:')) {
        featuredImage = line.replace(/^featuredImage:\s*/, '').trim();
      }
      i++;
    }
    i++; // Skip closing ---
  } else if (lines[0].startsWith('# ')) {
    title = lines[0].replace(/^#\s+/, '').trim();
    i = 1;
  }

  const body = lines.slice(i).join('\n').trim();
  return { meta: { title, featuredImage }, body };
}

function extractDateAndSlugFromPath(path: string): {
  date: string;
  slug: string;
} {
  const match = path.match(/(\d{4}-\d{2}-\d{2})-([^/]+)\.md$/);
  if (match) {
    return { date: match[1], slug: match[2] };
  }
  // Fallback: no date prefix
  const slug = path.split('/').pop()?.replace(/\.md$/, '') ?? 'post';
  return { date: new Date().toISOString().slice(0, 10), slug };
}

export function getAllPosts(): BlogPostMeta[] {
  const posts: BlogPostMeta[] = Object.entries(rawPosts).map(
    ([path, content]) => {
      const { meta } = parseFrontMatter(content);
      const { date, slug } = extractDateAndSlugFromPath(path);
      return {
        slug,
        date,
        title: meta.title || slug.replace(/-/g, ' '),
        featuredImage: meta.featuredImage,
      };
    }
  );
  return posts.sort((a, b) => (a.date < b.date ? 1 : -1));
}

export function getPostBySlug(slug: string): BlogPost | undefined {
  const entry = Object.entries(rawPosts).find(([path]) =>
    path.endsWith(`${slug}.md`)
  );
  if (!entry) return undefined;
  const [path, content] = entry;
  const { meta, body } = parseFrontMatter(content);
  const { date } = extractDateAndSlugFromPath(path);
  return {
    slug,
    date,
    title: meta.title || slug.replace(/-/g, ' '),
    featuredImage: meta.featuredImage,
    content: body,
  };
}
