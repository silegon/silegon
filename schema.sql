CREATE  TABLE IF NOT EXISTS silegon.tag (
      id_tag INT NOT NULL AUTO_INCREMENT ,
      slug VARCHAR(20) NULL ,
      name VARCHAR(20) NOT NULL ,
      count INT DEFAULT 1,
      PRIMARY KEY (id_tag) ,
      UNIQUE INDEX name_UNIQUE (name ASC) ,
      UNIQUE INDEX slug_UNIQUE (slug ASC) 
);

CREATE  TABLE IF NOT EXISTS silegon.post (
      id_post INT NOT NULL AUTO_INCREMENT ,
      title VARCHAR(45) NULL ,
      slug VARCHAR(45) NOT NULL ,
      content TEXT NULL ,
      content_html TEXT NULL ,
      content_format CHAR(1) DEFAULT 'R' ,
      content_status CHAR(1) DEFAULT 'P' ,
      publish_date DATE NULL ,
      PRIMARY KEY (id_post) ,
      UNIQUE INDEX title_UNIQUE (title ASC) ,
      UNIQUE INDEX slug_UNIQUE (slug ASC) 
);

CREATE  TABLE IF NOT EXISTS silegon.tag_post (
      id_tag INT NOT NULL ,
      id_post INT NOT NULL ,
      INDEX id_tag_index (id_tag ASC) ,
      INDEX id_post_index (id_post ASC) 
);
