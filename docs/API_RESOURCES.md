# API Resource Representations

## Channel Resource

```json
{
    "kind": "youtube#channel",
    "etag": etag,
    "id": string,
    "snippet": {
        "title": string,
        "description": string,
        "customUrl": string,
        "publishedAt": datetime,
        "thumbnails": {
        (key): {
            "url": string,
            "width": unsigned integer,
            "height": unsigned integer
        }
        },
        "defaultLanguage": string,
        "localized": {
        "title": string,
        "description": string
        },
        "country": string
    },
    "contentDetails": {
        "relatedPlaylists": {
        "likes": string,
        "favorites": string,
        "uploads": string
        }
    },
    "statistics": {
        "viewCount": unsigned long,
        "subscriberCount": unsigned long,  // this value is rounded to three significant figures
        "hiddenSubscriberCount": boolean,
        "videoCount": unsigned long
    },
    "topicDetails": {
        "topicIds": [
        string
        ],
        "topicCategories": [
        string
        ]
    },
    "status": {
        "privacyStatus": string,
        "isLinked": boolean,
        "longUploadsStatus": string,
        "madeForKids": boolean,
        "selfDeclaredMadeForKids": boolean
    },
    "brandingSettings": {
        "channel": {
        "title": string,
        "description": string,
        "keywords": string,
        "trackingAnalyticsAccountId": string,
        "moderateComments": boolean,
        "unsubscribedTrailer": string,
        "defaultLanguage": string,
        "country": string
        },
        "watch": {
        "textColor": string,
        "backgroundColor": string,
        "featuredPlaylistId": string
        }
    },
    "auditDetails": {
        "overallGoodStanding": boolean,
        "communityGuidelinesGoodStanding": boolean,
        "copyrightStrikesGoodStanding": boolean,
        "contentIdClaimsGoodStanding": boolean
    },
    "contentOwnerDetails": {
        "contentOwner": string,
        "timeLinked": datetime
    },
    "localizations": {
        (key): {
        "title": string,
        "description": string
        }
    }
}
```

## Channel Section resource

```json
{
  "kind": "youtube#channelSection",
  "etag": etag,
  "id": string,
  "snippet": {
    "type": string,
    "channelId": string,
    "title": string,
    "position": unsigned integer
  },
  "contentDetails": {
    "playlists": [
      string
    ],
    "channels": [
      string
    ]
  }
}
```

## Playlist Resource

```json
{
    "kind": "youtube#playlist",
    "etag": etag,
    "id": string,
    "snippet": {
        "publishedAt": datetime,
        "channelId": string,
        "title": string,
        "description": string,
        "thumbnails": {
        (key): {
            "url": string,
            "width": unsigned integer,
            "height": unsigned integer
        }
        },
        "channelTitle": string,
        "defaultLanguage": string,
        "localized": {
        "title": string,
        "description": string
        }
    },
    "status": {
        "privacyStatus": string
    },
    "contentDetails": {
        "itemCount": unsigned integer
    },
    "player": {
        "embedHtml": string
    },
    "localizations": {
        (key): {
        "title": string,
        "description": string
        }
    }
}
```

## Playlist Items Resource

```json
{
    "kind": "youtube#playlistItem",
    "etag": etag,
    "id": string,
    "snippet": {
        "publishedAt": datetime,
        "channelId": string,
        "title": string,
        "description": string,
        "thumbnails": {
        (key): {
            "url": string,
            "width": unsigned integer,
            "height": unsigned integer
        }
        },
        "channelTitle": string,
        "videoOwnerChannelTitle": string,
        "videoOwnerChannelId": string,
        "playlistId": string,
        "position": unsigned integer,
        "resourceId": {
        "kind": string,
        "videoId": string,
        }
    },
    "contentDetails": {
        "videoId": string,
        "startAt": string,
        "endAt": string,
        "note": string,
        "videoPublishedAt": datetime
    },
    "status": {
        "privacyStatus": string
    }
}
```

## Video Resource

```json
{
    "kind": "youtube#video",
    "etag": etag,
    "id": string,
    "snippet": {
        "publishedAt": datetime,
        "channelId": string,
        "title": string,
        "description": string,
        "thumbnails": {
        (key): {
            "url": string,
            "width": unsigned integer,
            "height": unsigned integer
        }
        },
        "channelTitle": string,
        "tags": [
            string
        ],
        "categoryId": string,
        "liveBroadcastContent": string,
        "defaultLanguage": string,
        "localized": {
            "title": string,
            "description": string
        },
        "defaultAudioLanguage": string
    },
    "contentDetails": {
        "duration": string,
        "dimension": string,
        "definition": string,
        "caption": string,
        "licensedContent": boolean,
        "regionRestriction": {
        "allowed": [
            string
        ],
        "blocked": [
            string
        ]
        },
        "contentRating": {
        "acbRating": string,
        "agcomRating": string,
        "anatelRating": string,
        "bbfcRating": string,
        "bfvcRating": string,
        "bmukkRating": string,
        "catvRating": string,
        "catvfrRating": string,
        "cbfcRating": string,
        "cccRating": string,
        "cceRating": string,
        "chfilmRating": string,
        "chvrsRating": string,
        "cicfRating": string,
        "cnaRating": string,
        "cncRating": string,
        "csaRating": string,
        "cscfRating": string,
        "czfilmRating": string,
        "djctqRating": string,
        "djctqRatingReasons": [,
            string
        ],
        "ecbmctRating": string,
        "eefilmRating": string,
        "egfilmRating": string,
        "eirinRating": string,
        "fcbmRating": string,
        "fcoRating": string,
        "fmocRating": string,
        "fpbRating": string,
        "fpbRatingReasons": [,
            string
        ],
        "fskRating": string,
        "grfilmRating": string,
        "icaaRating": string,
        "ifcoRating": string,
        "ilfilmRating": string,
        "incaaRating": string,
        "kfcbRating": string,
        "kijkwijzerRating": string,
        "kmrbRating": string,
        "lsfRating": string,
        "mccaaRating": string,
        "mccypRating": string,
        "mcstRating": string,
        "mdaRating": string,
        "medietilsynetRating": string,
        "mekuRating": string,
        "mibacRating": string,
        "mocRating": string,
        "moctwRating": string,
        "mpaaRating": string,
        "mpaatRating": string,
        "mtrcbRating": string,
        "nbcRating": string,
        "nbcplRating": string,
        "nfrcRating": string,
        "nfvcbRating": string,
        "nkclvRating": string,
        "oflcRating": string,
        "pefilmRating": string,
        "rcnofRating": string,
        "resorteviolenciaRating": string,
        "rtcRating": string,
        "rteRating": string,
        "russiaRating": string,
        "skfilmRating": string,
        "smaisRating": string,
        "smsaRating": string,
        "tvpgRating": string,
        "ytRating": string
        },
        "projection": string,
        "hasCustomThumbnail": boolean
    },
    "status": {
        "uploadStatus": string,
        "failureReason": string,
        "rejectionReason": string,
        "privacyStatus": string,
        "publishAt": datetime,
        "license": string,
        "embeddable": boolean,
        "publicStatsViewable": boolean,
        "madeForKids": boolean,
        "selfDeclaredMadeForKids": boolean
    },
    "statistics": {
        "viewCount": string,
        "likeCount": string,
        "dislikeCount": string,
        "favoriteCount": string,
        "commentCount": string
    },
    "player": {
        "embedHtml": string,
        "embedHeight": long,
        "embedWidth": long
    },
    "topicDetails": {
        "topicIds": [
        string
        ],
        "relevantTopicIds": [
        string
        ],
        "topicCategories": [
        string
        ]
    },
    "recordingDetails": {
        "recordingDate": datetime
    },
    "fileDetails": {
        "fileName": string,
        "fileSize": unsigned long,
        "fileType": string,
        "container": string,
        "videoStreams": [
        {
            "widthPixels": unsigned integer,
            "heightPixels": unsigned integer,
            "frameRateFps": double,
            "aspectRatio": double,
            "codec": string,
            "bitrateBps": unsigned long,
            "rotation": string,
            "vendor": string
        }
        ],
        "audioStreams": [
        {
            "channelCount": unsigned integer,
            "codec": string,
            "bitrateBps": unsigned long,
            "vendor": string
        }
        ],
        "durationMs": unsigned long,
        "bitrateBps": unsigned long,
        "creationTime": string
    },
    "processingDetails": {
        "processingStatus": string,
        "processingProgress": {
        "partsTotal": unsigned long,
        "partsProcessed": unsigned long,
        "timeLeftMs": unsigned long
        },
        "processingFailureReason": string,
        "fileDetailsAvailability": string,
        "processingIssuesAvailability": string,
        "tagSuggestionsAvailability": string,
        "editorSuggestionsAvailability": string,
        "thumbnailsAvailability": string
    },
    "suggestions": {
        "processingErrors": [
        string
        ],
        "processingWarnings": [
        string
        ],
        "processingHints": [
        string
        ],
        "tagSuggestions": [
        {
            "tag": string,
            "categoryRestricts": [
            string
            ]
        }
        ],
        "editorSuggestions": [
        string
        ]
    },
    "liveStreamingDetails": {
        "actualStartTime": datetime,
        "actualEndTime": datetime,
        "scheduledStartTime": datetime,
        "scheduledEndTime": datetime,
        "concurrentViewers": unsigned long,
        "activeLiveChatId": string
    },
    "localizations": {
        (key): {
        "title": string,
        "description": string
        }
    }
}
```
## Activity Resource

```json
{
    "kind": "youtube#activity",
    "etag": etag,
    "id": string,
    "snippet": {
        "publishedAt": datetime,
        "channelId": string,
        "title": string,
        "description": string,
        "thumbnails": {
        (key): {
            "url": string,
            "width": unsigned integer,
            "height": unsigned integer
        }
        },
        "channelTitle": string,
        "type": string,
        "groupId": string
    },
    "contentDetails": {
        "upload": {
        "videoId": string
        },
        "like": {
        "resourceId": {
            "kind": string,
            "videoId": string,
        }
        },
        "favorite": {
        "resourceId": {
            "kind": string,
            "videoId": string,
        }
        },
        "comment": {
        "resourceId": {
            "kind": string,
            "videoId": string,
            "channelId": string,
        }
        },
        "subscription": {
        "resourceId": {
            "kind": string,
            "channelId": string,
        }
        },
        "playlistItem": {
        "resourceId": {
            "kind": string,
            "videoId": string,
        },
        "playlistId": string,
        "playlistItemId": string
        },
        "recommendation": {
        "resourceId": {
            "kind": string,
            "videoId": string,
            "channelId": string,
        },
        "reason": string,
        "seedResourceId": {
            "kind": string,
            "videoId": string,
            "channelId": string,
            "playlistId": string
        }
        },
        "social": {
        "type": string,
        "resourceId": {
            "kind": string,
            "videoId": string,
            "channelId": string,
            "playlistId": string
        },
        "author": string,
        "referenceUrl": string,
        "imageUrl": string
        },
        "channelItem": {
        "resourceId": {
        }
        },
    }
}
```

## Search Resource

```json
{
    "kind": "youtube#searchResult",
    "etag": etag,
    "id": {
        "kind": string,
        "videoId": string,
        "channelId": string,
        "playlistId": string
    },
    "snippet": {
        "publishedAt": datetime,
        "channelId": string,
        "title": string,
        "description": string,
        "thumbnails": {
        (key): {
            "url": string,
            "width": unsigned integer,
            "height": unsigned integer
        }
        },
        "channelTitle": string,
        "liveBroadcastContent": string
    }
}
```

## Caption Resource

```json
{
    "kind": "youtube#caption",
    "etag": etag,
    "id": string,
    "snippet": {
        "videoId": string,
        "lastUpdated": datetime,
        "trackKind": string,
        "language": string,
        "name": string,
        "audioTrackType": string,
        "isCC": boolean,
        "isLarge": boolean,
        "isEasyReader": boolean,
        "isDraft": boolean,
        "isAutoSynced": boolean,
        "status": string,
        "failureReason": string
    }
}
```

## Channel Banner Resource

```json
{
    "kind": "youtube#channelBannerResource",
    "etag": etag,
    "url": string
}
```

## Comments Resource

```json
{
    "kind": "youtube#comment",
    "etag": etag,
    "id": string,
    "snippet": {
        "authorDisplayName": string,
        "authorProfileImageUrl": string,
        "authorChannelUrl": string,
        "authorChannelId": {
        "value": string
        },
        "channelId": string,
        "videoId": string,
        "textDisplay": string,
        "textOriginal": string,
        "parentId": string,
        "canRate": boolean,
        "viewerRating": string,
        "likeCount": unsigned integer,
        "moderationStatus": string,
        "publishedAt": datetime,
        "updatedAt": datetime
    }
}
```

## Comment Threads Resource

```json
{
    "kind": "youtube#commentThread",
    "etag": etag,
    "id": string,
    "snippet": {
        "channelId": string,
        "videoId": string,
        "topLevelComment": comments Resource,
        "canReply": boolean,
        "totalReplyCount": unsigned integer,
        "isPublic": boolean
    },
    "replies": {
        "comments": [
        comments Resource
        ]
    }
}
```

## Subscriptions Resource

```json
{
    "kind": "youtube#subscription",
    "etag": etag,
    "id": string,
    "snippet": {
        "publishedAt": datetime,
        "channelTitle": string,
        "title": string,
        "description": string,
        "resourceId": {
        "kind": string,
        "channelId": string,
        },
        "channelId": string,
        "thumbnails": {
        (key): {
            "url": string,
            "width": unsigned integer,
            "height": unsigned integer
        }
        }
    },
    "contentDetails": {
        "totalItemCount": unsigned integer,
        "newItemCount": unsigned integer,
        "activityType": string
    },
    "subscriberSnippet": {
        "title": string,
        "description": string,
        "channelId": string,
        "thumbnails": {
        (key): {
            "url": string,
            "width": unsigned integer,
            "height": unsigned integer
        }
        }
    }
}
```

## Thumbnail Resource

```json
{
    "default": {
        "url": string,
        "width": unsigned integer,
        "height": unsigned integer
    },
    "medium": {
        "url": string,
        "width": unsigned integer,
        "height": unsigned integer
    },
    "high": {
        "url": string,
        "width": unsigned integer,
        "height": unsigned integer
    },
    "standard": {
        "url": string,
        "width": unsigned integer,
        "height": unsigned integer
    },
    "maxres": {
        "url": string,
        "width": unsigned integer,
        "height": unsigned integer
    }
}
```

## Members Resource

```json
{
    "kind": "youtube#member",
    "etag": etag,
    "snippet": {
        "creatorChannelId": string,
        "memberDetails": {
        "channelId": string,
        "channelUrl": string,
        "displayName": string,
        "profileImageUrl": string
        },
        "membershipsDetails": {
        "highestAccessibleLevel": string,
        "highestAccessibleLevelDisplayName": string,
        "accessibleLevels": [
            string
        ],
        "membershipsDuration": {
            "memberSince": datetime,
            "memberTotalDurationMonths": integer,
        },
        "membershipsDurationAtLevel": [
            {
            "level": string,
            "memberSince": datetime,
            "memberTotalDurationMonths": integer,
            }
        ]
        }
    }
}
```

## Membership Levels Resource

```json
{
    "kind": "youtube#membershipsLevel",
    "etag": etag,
    "id": string,
    "snippet": {
        "creatorChannelId": string,
        "levelDetails": {
        "displayName": string,
        }
    }
}
```

## Video Abuse Report Reasons Resource

```json
{
    "kind": "youtube#videoAbuseReportReason",
    "etag": etag,
    "id": string,
    "snippet": {
        "label": string,
        "secondaryReasons": [
        {
            "id": string,
            "label": string
        }
        ]
    }
}
```

## Video Categories Resource

```json
{
    "kind": "youtube#videoCategory",
    "etag": etag,
    "id": string,
    "snippet": {
        "channelId": "UCBR8-60-B28hp2BmDPdntcQ",
        "title": string,
        "assignable": boolean
    }
}
```

## WaterMarks Resource

```json
{
    "timing": {
        "type": string,
        "offsetMs": unsigned long,
        "durationMs": unsigned long
    },
    "position": {
        "type": string,
        "cornerPosition": string
    },
    "imageUrl": string,
    "imageBytes": bytes,
    "targetChannelId": string
}

```
