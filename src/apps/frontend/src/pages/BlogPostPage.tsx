import React, { useMemo } from 'react';
import { useParams, Link } from 'react-router-dom';
import { getPostBySlug } from '@/lib/blog';
import { AnimatedBackground } from '@/components/landing/components/Background';
import { Header } from '@/components/landing/components/Header';
import styles from '@/components/landing/styles/Blog.module.css';

// Minimal Markdown renderer: only headings, paragraphs, lists, code blocks
function renderMarkdown(md: string): React.ReactNode {
  const lines = md.split('\n');
  const elements: React.ReactNode[] = [];
  let inCode = false;
  let codeBuffer: string[] = [];
  let listBuffer: string[] = [];

  const flushCode = () => {
    if (codeBuffer.length) {
      elements.push(
        <pre
          key={`code-${elements.length}`}
          style={{ background: '#f6f8fa', padding: '1rem', overflowX: 'auto' }}
        >
          <code>{codeBuffer.join('\n')}</code>
        </pre>
      );
      codeBuffer = [];
    }
  };

  const flushList = () => {
    if (listBuffer.length) {
      elements.push(
        <ul key={`list-${elements.length}`}>
          {listBuffer.map((item, idx) => (
            <li key={idx}>{item}</li>
          ))}
        </ul>
      );
      listBuffer = [];
    }
  };

  for (const rawLine of lines) {
    const line = rawLine.replace(/\r$/, '');
    if (line.trim().startsWith('```')) {
      if (inCode) {
        inCode = false;
        flushCode();
      } else {
        inCode = true;
      }
      continue;
    }
    if (inCode) {
      codeBuffer.push(line);
      continue;
    }
    if (/^\s*[-*]\s+/.test(line)) {
      listBuffer.push(line.replace(/^\s*[-*]\s+/, ''));
      continue;
    } else {
      flushList();
    }
    if (line.startsWith('# ')) {
      elements.push(
        <h1 key={`h1-${elements.length}`}>{line.slice(2).trim()}</h1>
      );
    } else if (line.startsWith('## ')) {
      elements.push(
        <h2 key={`h2-${elements.length}`}>{line.slice(3).trim()}</h2>
      );
    } else if (line.trim() === '') {
      elements.push(
        <div key={`sp-${elements.length}`} style={{ height: '0.5rem' }} />
      );
    } else {
      elements.push(<p key={`p-${elements.length}`}>{line}</p>);
    }
  }
  flushList();
  flushCode();
  return elements;
}

const BlogPostPage: React.FC = () => {
  const { slug = '' } = useParams();
  const post = useMemo(() => getPostBySlug(slug), [slug]);

  if (!post) {
    return (
      <div className={styles.blogPage}>
        <AnimatedBackground />
        <Header />
        <main className={styles.container}>
          <div className={styles.contentContainer}>
            <p>Post not found.</p>
            <p>
              <Link to="/blog">Back to Blog</Link>
            </p>
          </div>
        </main>
      </div>
    );
  }

  return (
    <div className={styles.blogPage}>
      <AnimatedBackground />
      <Header />
      <main className={styles.container}>
        <div className={styles.contentContainer}>
          <p className={styles.meta}>{post.date}</p>
          <h1 className={styles.title}>{post.title}</h1>
          {post.featuredImage && (
            <img
              src={post.featuredImage}
              alt={post.title}
              className={styles.featuredImage}
            />
          )}
          <article className={styles.article}>
            {renderMarkdown(post.content)}
          </article>
          <p className={styles.backLink}>
            <Link to="/blog">← Back to Blog</Link>
          </p>
        </div>
      </main>
    </div>
  );
};

export default BlogPostPage;
