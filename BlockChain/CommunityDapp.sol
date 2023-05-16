// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;
contract CommunityDapp 
{
    struct User {
        string name;
        uint joinedTimestamp;
        bool registered;
    }
    struct Post {
        uint256 id;  
        address author;
        string content;
        uint timestamp;
    }
    struct Comment{
        uint256 postId;
        uint256 commentId;  
        string username; 
        address author; 
        string content; 
        uint timestamp;
    }
    struct Like{
        uint256 postId; 
        uint256 likeId; 
        string username; 
        uint timestamp;  
    }
    struct UserWithPosts {
        address userAddress; 
        string username;
        Post[] posts;
        uint postCount;
    }
    mapping(address => User) private users;
    mapping(address => mapping(uint256 => bool)) userLikedPosts;
    Post[] private posts; 
    Comment[] private comments;  
    Like[] private likes; 
    uint256 private id_posts =1;
    uint256 private id_comments =1 ;  
    uint private id_likes = 1 ;  
    function register(string memory name) public {
        require(!users[msg.sender].registered, "User already registered");
        User memory newUser = User(name, block.timestamp, true);
        users[msg.sender] = newUser;
    }

    function post(string memory content) public {
        require(users[msg.sender].registered, "User not registered");

        Post memory newPost = Post(id_posts,msg.sender, content, block.timestamp); 
        id_posts ++ ; 
        posts.push(newPost);
    }
    function comment(uint256 _postId , string memory _comment ) public {
        require(users[msg.sender].registered, "User not registered");
        Comment memory newComment = Comment(_postId,id_comments, users[msg.sender].name , msg.sender,_comment , block.timestamp);
        comments.push(newComment); 
        id_comments++  ; 
    }
    function like(uint256 _postId ) public 
    {
        require(users[msg.sender].registered, "User not registered");  
        require(!userLikedPosts[msg.sender][_postId], "User already liked this post");
        Like memory newLike = Like(_postId , id_likes , users[msg.sender].name, block.timestamp); 
        likes.push(newLike); 
        id_likes ++; 
        userLikedPosts[msg.sender][_postId] = true;
                                 
    }
    function GetLikesOnPost(uint256 _PostId) public view returns(Like[] memory ){
    uint count= 0 ; 
    uint likesCount=0 ; 
    for (uint i = 0; i < likes.length; i++) {
        if(likes[i].postId == _PostId )
        {
            likesCount ++ ; 
        }
     }
    Like[] memory LikesForPost = new Like[](likesCount);  
    for (uint i = 0; i < likes.length; i++) {
        if(likes[i].postId == _PostId )
        {
            LikesForPost[count].postId = likes[i].postId; 
            LikesForPost[count].likeId = likes[i].likeId; 
            LikesForPost[count].username = likes[i].username;
            LikesForPost[count].timestamp = likes[i].timestamp;  
            count ++;   
        }
     }
     return LikesForPost ; 
    }
    function GetCommentsOnPost(uint256 _PostId  ) public view returns(Comment[] memory) {
        uint count = 0 ; 
        uint commentsCount = 0 ;
        for (uint i = 0; i < comments.length; i++) {
         if(comments[i].postId == _PostId){
             commentsCount++; 
         }
         }
        Comment[] memory CommentsForPost = new Comment[](commentsCount);   
        for (uint i = 0; i < comments.length; i++) {
            if(comments[i].postId == _PostId){
                CommentsForPost[count].postId = comments[i].postId;
                CommentsForPost[count].commentId= comments[i].commentId;
                CommentsForPost[count].username= comments[i].username;
                CommentsForPost[count].author =comments[i].author;
                CommentsForPost[count].content = comments[i].content;
                CommentsForPost[count].timestamp = comments[i].timestamp;
                count++; 
            }
        }

        return CommentsForPost; 
    } 
    function getUser(address userAddress) public view returns (User memory) {
        return users[userAddress];
    }

    function getPosts() public view returns (Post[] memory) {
        return posts;
    }

    function getUsersWithPosts() public view returns (UserWithPosts[] memory) {
        UserWithPosts[] memory result = new UserWithPosts[](posts.length);
        uint count = 0;

        for (uint i = 0; i < posts.length; i++) {
            Post memory currentPost = posts[i];
            User memory currentUser = users[currentPost.author];
            string memory username = currentUser.name ; 
            bool userFound = false;

            for (uint j = 0; j < count; j++) {
                if (result[j].userAddress == currentPost.author) {
                    result[j].posts[result[j].postCount] = currentPost;
                    result[j].postCount++;
                    userFound = true;
                    break;
                }
            }

            if (!userFound) {
                UserWithPosts memory newUserWithPosts;
                newUserWithPosts.userAddress = currentPost.author;
                newUserWithPosts.username = username;
                newUserWithPosts.posts = new Post[](posts.length);
                newUserWithPosts.posts[0] = currentPost;
                newUserWithPosts.postCount = 1;
                result[count] = newUserWithPosts;
                count++;
            }
        }
        return result;
    }
}