var script = {
    {
        "name":"opening",
        "background": "landscape.svg",
        "action-type": "delay",
        "delay": 5000,
        "followed-by": "girl-intro-1"
    },
    {
        "name":"girl-intro-1",
        "objects-add": [
            {
                "name": "girl-speaking",
                "image": "girl-speaking.png",
                "position": 
                    {
                        "point": "left-bottom",
                        "x": 10,
                        "y": 90
                    },
                "on-complete": "delete"
            }
        ]
        "action-type": "play-audio",
        "audio": "girl-intro.aac",
        "followed-by": "red-button-intro"
          
    },
    {
        "name": "red-button-intro",
        "objects-add": [
            {
                "name": "red-button",
                "image": "red-button.png",
                "position": 
                    {
                        "point": "center",
                        "x": 45,
                        "y": 90
                    }
            },
            {
                "name": "girl-silent",
                "image": "girl-silent.png",
                "position": 
                    {
                        "point": "left-bottom",
                        "x": 10,
                        "y": 90
                    },
                "on-complete": "delete"
            }            
        ],
        "action-type": "delay",
        "delay": 2000,        
        "followed-by": "girl-intro-2"
    },
    {
        "name":"girl-intro-1",
        "objects-add": [
            {
                "name": "girl-speaking",
                "image": "girl-speaking.png",
                "position": 
                    {
                        "point": "left-bottom",
                        "x": 10,
                        "y": 90
                    }
            }
        ]
        "action-type": "play-audio",
        "audio": "girl-intro.aac",
        "followed-by": "red-button-intro"
          
    },    
};
