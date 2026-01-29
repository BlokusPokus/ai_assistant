import React from 'react';
import { Link } from 'react-router-dom';
import { getAllPosts } from '@/lib/blog';
import { AnimatedBackground } from '@/components/landing/components/Background';
import { Header } from '@/components/landing/components/Header';
import styles from '@/components/landing/styles/Blog.module.css';

const BlogPage: React.FC = () => {
  const posts = getAllPosts();
  return (
    <div className={styles.blogPage}>
      <AnimatedBackground />
      <Header />
      <main className={styles.container}>
        <div className={styles.contentContainer}>
          <h1 className={styles.title}>Blog</h1>
          {posts.length === 0 ? (
            <p className={styles.meta}>
              No posts yet. Add Markdown files to <code>src/content/blog</code>.
            </p>
          ) : (
            <ul className={styles.list}>
              {posts.map(post => (
                <li key={post.slug} className={styles.listItem}>
                  {post.featuredImage && (
                    <img
                      src={post.featuredImage}
                      alt={post.title}
                      className={styles.postImage}
                    />
                  )}
                  <div className={styles.postContent}>
                    <Link to={`/blog/${post.slug}`} className={styles.postLink}>
                      {post.title}
                    </Link>
                    <div className={styles.meta}>{post.date}</div>
                  </div>
                </li>
              ))}
            </ul>
          )}
        </div>
      </main>
    </div>
  );
};

export default BlogPage;
