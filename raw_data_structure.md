# Raw Data Structure

This file explains how the raw input data is stored under `data/raw/`.

The goal is to keep one place where the project can describe:

- how the raw folders are organized
- which raw files are actually important
- what each raw file contains in simple terms
- what one representative entry looks like

Representative samples below are sanitized. They show the real structure, but personal content is shortened or replaced with placeholders where needed.

## Folder Rename Summary

These raw folders were renamed to make the structure more conventional and easier to read:

| Old name | New name |
| --- | --- |
| `CHATGPT_DATA` | `chatgpt_export` |
| `Twitter_DATA` | `twitter_archive` |
| `PrimeVideoData` | `prime_video` |
| `Netflix` | `netflix` |
| `instagram-nomer_karaca-2026-03-16-TnAQ86H2` | `instagram_export` |
| `nihatomer.karaca_YOUTUBE` | `youtube_account_nihatomer_karaca` |
| `omer.karaca_YOUTUBE` | `youtube_account_omer_karaca` |
| `omer.karaca_spotify` | `spotify_account_omer_karaca` |
| `MyActivity.html` at raw root | `youtube_legacy/MyActivity.html` |

## Top-Level Raw Folder Tree

```text
data/raw/
|- academical_calendar/
|- chatgpt_export/
|- instagram_export/
|- netflix/
|- prime_video/
|- spotify_account_omer_karaca/
|- twitter_archive/
|- youtube_account_nihatomer_karaca/
|- youtube_account_omer_karaca/
|- youtube_legacy/
```

## Data

### Academic Calendar

#### Raw folder structure

```text
data/raw/
`- academical_calendar/
   `- academicCalendar.jsonl
```

#### `academicCalendar.jsonl`

This file is a line-delimited JSON dataset where each row represents one academic term. It is not platform behavior data; it is a support dataset used to define semester structure, week starts, add-drop dates, and final exam periods.

This matters because it gives the project a real calendar backbone for academic-pressure labeling instead of relying only on manual date guesses.

Sample entry:

```json
{
  "academic_year": "2025-2026",
  "term": "spring",
  "population": "undergraduate",
  "term_start_date": "2026-02-16",
  "add_drop_start_date": "2026-02-26",
  "add_drop_end_date": "2026-02-27",
  "final_exam_start_date": "2026-06-01",
  "final_exam_end_date": "2026-06-10",
  "week_1_start": "2026-02-16",
  "week_2_start": "2026-02-23",
  "week_3_start": "2026-03-02",
  "notes": "Ramadan holiday / spring break was listed on the page."
}
```

### YouTube

#### Raw folder structure

```text
data/raw/
|- youtube_account_nihatomer_karaca/
|  `- YouTube and YouTube Music/
|     |- history/
|     |  |- watch-history.html
|     |  `- search-history.html
|     `- subscriptions/
|        `- subscriptions.csv
|- youtube_account_omer_karaca/
|  `- YouTube and YouTube Music/
|     |- history/
|     |  |- watch-history.html
|     |  `- search-history.html
|     `- subscriptions/
|        `- subscriptions.csv
`- youtube_legacy/
   `- MyActivity.html
```

#### `watch-history.html`

This is a Google My Activity HTML export. It stores repeated activity blocks rather than a ready-made table, so each watch event has to be parsed from the page structure.

Each block usually contains the service name, an action like `Watched`, the video title link, the channel link, and a timestamp.

Sample entry:

```json
{
  "service": "YouTube",
  "action": "Watched",
  "primary_text": "<video title>",
  "primary_url": "https://www.youtube.com/watch?v=...",
  "secondary_text": "<channel name>",
  "timestamp_text": "Mar 15, 2026, 8:38:46 PM GMT+03:00"
}
```

#### `search-history.html`

This has the same HTML-style export structure as watch history, but the action is usually `Searched for`. It is useful for understanding what was searched, when, and from which account export it came.

Sample entry:

```json
{
  "service": "YouTube",
  "action": "Searched for",
  "primary_text": "<search query>",
  "primary_url": "https://www.youtube.com/results?search_query=...",
  "timestamp_text": "Mar 15, 2026, 8:38:44 PM GMT+03:00"
}
```

#### `subscriptions/subscriptions.csv`

This is the cleanest YouTube raw file because it is already tabular. Each row is one subscribed channel with a channel ID, a channel URL, and a display title.

Sample entry:

```json
{
  "Channel Id": "UCxxxxxxxxxxxxxxxxxxxxxx",
  "Channel Url": "http://www.youtube.com/channel/UCxxxxxxxxxxxxxxxxxxxxxx",
  "Channel Title": "<channel title>"
}
```

#### `youtube_legacy/MyActivity.html`

This is an older general Google My Activity export kept as a fallback. It has the same repeated-block structure as the account-specific exports and is useful when newer Takeout folders miss older rows.

Sample entry:

```json
{
  "service": "YouTube",
  "action": "Watched",
  "primary_text": "<video title>",
  "secondary_text": "<channel name>",
  "timestamp_text": "Mar 14, 2026, 9:16:53 PM GMT+03:00"
}
```

### Spotify

#### Raw folder structure

```text
data/raw/
`- spotify_account_omer_karaca/
   `- Spotify Extended Streaming History/
      |- ReadMeFirst_ExtendedStreamingHistory.pdf
      |- Streaming_History_Audio_2019-2020_0.json
      |- Streaming_History_Audio_2020-2021_1.json
      |- ...
      `- Streaming_History_Video_2024-2026.json
```

#### `Streaming_History_*.json`

These files are JSON arrays where each object is one playback event. Spotify raw data is strong because it already contains exact playback duration through `ms_played`.

Each row usually includes the end timestamp, platform, country, playback duration, track metadata, and playback state fields such as `shuffle` or `skipped`.

Sample entry:

```json
{
  "ts": "2019-07-27T07:57:46Z",
  "platform": "iOS 12.1 (iPhone9,1)",
  "ms_played": 4783,
  "conn_country": "TR",
  "master_metadata_track_name": "<track title>",
  "master_metadata_album_artist_name": "<artist>",
  "master_metadata_album_album_name": "<album>",
  "spotify_track_uri": "spotify:track:...",
  "reason_start": "clickrow",
  "reason_end": "endplay",
  "shuffle": false,
  "skipped": false
}
```

#### `ReadMeFirst_ExtendedStreamingHistory.pdf`

This is vendor documentation that comes with the Spotify export. It does not contain behavioral rows, but it helps explain the meaning of the export files and fields.

### Instagram

#### Raw folder structure

```text
data/raw/
`- instagram_export/
   |- logged_information/
   |- media/
   |- personal_information/
   |- preferences/
   `- your_instagram_activity/
      |- likes/
      |- media/
      |- messages/
      |- other_activity/
      |- saved/
      `- story_interactions/
```

`instagram_export/` contains both account-level context folders and the main activity folder. For project analysis, `your_instagram_activity/` is the most important subtree.

#### `your_instagram_activity/likes/`

This folder contains likes on posts and comments. It is useful as timestamped interaction data, but it is not a direct screen-time export.

Sample entry shape:

```json
{
  "title": "<liked account or item>",
  "media": [
    {
      "uri": "https://www.instagram.com/..."
    }
  ],
  "timestamp": 1700000000
}
```

#### `your_instagram_activity/saved/`

This folder stores saved posts or reels. It tells us what was intentionally saved and when that action happened.

Sample entry:

```json
{
  "title": "<account or post title>",
  "string_map_data": {
    "Saved on": {
      "href": "https://www.instagram.com/reel/...",
      "timestamp": 1772831883
    }
  }
}
```

#### `your_instagram_activity/story_interactions/`

This folder contains interactive story events such as story likes, polls, quizzes, emoji sliders, and similar actions. These are timestamped events and are useful because they reflect active engagement, not just passive viewing.

Sample entry:

```json
{
  "title": "<story owner>",
  "string_list_data": [
    {
      "timestamp": 1773512376
    }
  ]
}
```

#### `your_instagram_activity/media/`

This folder contains content creation records such as posts and stories. It helps show when content was created or uploaded rather than just consumed.

Sample entry:

```json
{
  "title": "",
  "creation_timestamp": 1744841335,
  "media": [
    {
      "uri": "media/posts/202504/17904019260137620.jpg",
      "creation_timestamp": 1744841333,
      "title": ""
    }
  ]
}
```

#### `your_instagram_activity/messages/`

This folder contains thread folders, and each thread contains one or more `message_*.json` files. Message objects can hold text, call duration, photos, shared posts, audio, and other DM event types.

Sample entry:

```json
{
  "sender_name": "<sender>",
  "timestamp_ms": 1729763520318,
  "content": "<message text>",
  "call_duration": null,
  "photos": null,
  "share": null
}
```

#### `your_instagram_activity/other_activity/`

This folder stores miscellaneous interaction records such as surveys. It is not the main behavioral signal, but it is still part of the export and can hold timestamped activity context.

Sample entry:

```json
{
  "label": "<activity label>",
  "description": "<activity description>",
  "vec": [
    {
      "dict": [
        {
          "label": "<field name>",
          "value": "<field value>"
        }
      ]
    }
  ]
}
```

### Twitter

#### Raw folder structure

```text
data/raw/
`- twitter_archive/
   `- twitter-<archive-id>/
      |- Your archive.html
      |- assets/
      `- data/
         |- account.js
         |- tweets.js
         |- deleted-tweets.js
         |- like.js
         |- direct-messages.js
         |- direct-messages-group.js
         |- audio-video-calls-in-dm.js
         |- audio-video-calls-in-dm-recipient-sessions.js
         |- spaces-metadata.js
         |- follower.js
         `- following.js
```

Twitter raw exports use JavaScript wrapper files, not plain JSON. Each file begins with a variable assignment, and the actual payload is inside that wrapper.

#### `account.js`

This file contains account identity metadata. It is the anchor that tells us which username, account ID, email, and display name belong to the rest of the archive.

Sample entry:

```json
{
  "username": "merNihatKaraca1",
  "accountId": "1079449933944623104",
  "email": "nihatomer.karaca@gmail.com",
  "accountDisplayName": "<display name>",
  "createdAt": "2018-12-30T18:51:34.243Z"
}
```

#### `tweets.js` and `deleted-tweets.js`

These files contain posted tweets and deleted tweets. Each item usually carries tweet text, creation time, language, source app, and engagement counts captured by the archive.

Sample entry:

```json
{
  "id": "2013643718620799191",
  "created_at": "Tue Jan 20 16:04:08 +0000 2026",
  "full_text": "<tweet text>",
  "favorite_count": "0",
  "retweet_count": "0",
  "lang": "tr",
  "source": "<a href=\"http://twitter.com/download/iphone\">Twitter for iPhone</a>"
}
```

#### `like.js`

This file contains liked tweets, but in this archive it does not contain per-like timestamps. It is good for liked-content inventory, not for day-level timing analysis.

Sample entry:

```json
{
  "tweetId": "2032900841061949725",
  "fullText": "<liked tweet text>",
  "expandedUrl": "https://twitter.com/i/web/status/2032900841061949725"
}
```

#### `direct-messages.js` and `direct-messages-group.js`

These files contain DM conversation events. They are not only plain text messages; they can also include membership changes, URLs, media links, and other conversation events.

Direct-message sample:

```json
{
  "id": "1822309685556326631",
  "createdAt": "2024-08-10T16:31:00.634Z",
  "senderId": "3957016521",
  "recipientId": "1079449933944623104",
  "text": "<message text>",
  "urls": [
    {
      "url": "https://t.co/...",
      "expanded": "https://twitter.com/..."
    }
  ]
}
```

Group-message event sample:

```json
{
  "participantsLeave": {
    "userIds": [
      "1497169821120749572"
    ],
    "createdAt": "2023-02-07T09:06:45.921Z"
  }
}
```

#### `audio-video-calls-in-dm*.js` and `spaces-metadata.js`

These files are reserved for call and Space metadata. In the current archive they exist structurally, but the processed layer currently finds zero usable rows, so the raw payload behaves like an empty list.

Sample entry:

```json
[]
```

### Netflix

#### Raw folder structure

```text
data/raw/
`- netflix/
   `- NetflixViewingHistory.csv
```

#### `NetflixViewingHistory.csv`

This is the simplest raw input in the project. Each row is one viewing-history record with only a title and a date.

Sample entry:

```json
{
  "Title": "<movie or episode title>",
  "Date": "3/10/26"
}
```

### Prime Video

#### Raw folder structure

```text
data/raw/
`- prime_video/
   |- Prime Video_ watchshistory.pdf
   `- raw.txt
```

#### `raw.txt`

This is the main Prime Video raw source used by the parser. It is not a clean CSV or JSON export; it is copied text from a paginated document, so records must be reconstructed from date headings and watch-history text lines.

Representative text block:

```text
19 Mart 2026 Perşembe
Supernatural -
Sezon 13 İzleme Geçmişi'nden bölümleri sil
İzlenen bölümler
18. Bölüm: Bring 'em Back Alive
17. Bölüm: The Thing
16. Bölüm: Scoobynatural
15. Bölüm: A Most Holy Man
```

#### `Prime Video_ watchshistory.pdf`

This is a source copy of the original document behind the pasted text. It is useful for manual checking when the text reconstruction is ambiguous.

### ChatGPT

#### Raw folder structure

```text
data/raw/
`- chatgpt_export/
   |- chat.html
   |- conversations-000.json
   |- conversations-001.json
   |- ...
   |- export_manifest.json
   |- shared_conversations.json
   |- user.json
   |- user_settings.json
   |- dalle-generations/
   |- user-<id>/
   |- <conversation-id>/
   `- file-*
```

This export is the largest and most mixed raw folder in the project. It contains both structured conversation data and many attachment files such as images, audio, and exported documents.

#### `chat.html`

This is the main parser input currently used by the project. It embeds JavaScript data blobs that contain conversation data and attachment mappings.

Representative conversation entry shape:

```json
{
  "id": "001e6970-be11-4ad0-8dd5-8cfb09590b3e",
  "title": "Int Sum and Output",
  "create_time": 1709744608.701726,
  "update_time": 1709744681.916281,
  "default_model_slug": null,
  "current_node": "32f267fb-363c-4086-b4bc-f538c9f73494"
}
```

#### `conversations-*.json`

These files are conversation shards. They store conversation objects in a more directly machine-readable JSON form than `chat.html`, but the project currently documents and parses the HTML export as the main source.

Sample entry:

```json
{
  "id": "<conversation id>",
  "title": "<conversation title>",
  "create_time": 1709744608.701726,
  "update_time": 1709744681.916281,
  "current_node": "<node id>"
}
```

#### `export_manifest.json`

This file is a manifest of exported files. It tells us which attachment paths exist and how large they are.

Sample entry:

```json
{
  "export_files": [
    {
      "path": "00ca4c9a...#p_6.jpg-p_6.jpg",
      "size_bytes": 40278
    }
  ]
}
```

#### `shared_conversations.json`

This file stores metadata about conversations that were shared publicly or exported as shared items. It is supporting metadata rather than the main message timeline.

#### `user.json` and `user_settings.json`

These files contain account-level metadata and settings. They are useful for export context, but they are not the main behavioral table.

Sample entry:

```json
{
  "birth_year": 2003,
  "chatgpt_plus_user": true,
  "email": "nihatomer.karaca@gmail.com",
  "id": "user-..."
}
```

#### Attachment folders and files

The remaining folders and files hold exported assets. That includes generated images, uploaded files, conversation-specific image/audio folders, and user asset folders.

Common examples:

- `dalle-generations/`: generated images
- `<conversation-id>/audio` and `<conversation-id>/image`: conversation-scoped media
- `file-*`: top-level exported files attached to chats
- `user-<id>/`: user-scoped exported assets

## Notes For Future Updates

- Keep this file updated whenever a raw export folder is renamed or a new platform is added.
- If a new raw file type appears, add it under the correct platform section with:
  - where it lives
  - what it contains
  - why it matters
  - one small representative sample
- If the project starts using a new raw file as a primary source, move that file description higher in its platform section.
