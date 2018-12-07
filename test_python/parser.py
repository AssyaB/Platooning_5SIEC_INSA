

test = 'SPE:25;SPE:10;STE:left;STE:right;STE:stop;MOV:stop;MOV:forward;MOV:backward;PLA:on;PLA:off;UFL:123;UFR:234;URC:345;URL:456;URR:567;UFC:678;POS:789;BAT:8901;SWL:9012;SWR:1234;YAW:23.45;PIT:34.56;ROL:45.67;'
speed_cmd = 0
move = 0
turn = 0
enable = 0

#split each command received if there are more of 1 
for cmd in test.split(';'):
    print('val cmd : ',cmd)
    
    # don't try an empty command
    if not cmd: continue 
    
    #split the dealed command in header and payload (command = 'header:payload;')
    header, payload = cmd.split(':')
    print("header :", header, " payload:", payload)
    
    #Deal with the command
    if (header == 'SPE'):  # speed
        speed_cmd = int(payload)
        print("speed is updated to ", speed_cmd)
    elif (header == 'STE'):  # steering
        if (payload == 'left'):
            turn = -1
            enable = 1
            print("send cmd turn left")
        elif (payload == 'right'):
            turn = 1
            enable = 1
            print("send cmd turn right")
        elif (payload == 'stop'):
            turn = 0
            enable = 0
            print("send cmd stop to turn")
    elif (header == 'MOV'):  # move
        if (payload == 'stop'):
            move = 0
            enable = 0
            print("send cmd move stop")
        elif (payload == 'forward'):
            print("send cmd move forward")
            move = 1
            enable = 1
        elif (payload == 'backward'):
            print("send cmd move backward")
            move = -1
            enable = 1
    elif (header == 'PLA'): # Platooning
        if (payload == 'on'):
            print("starting platooning mode")
        if (payload == 'off'):
            print("stopping platooning mode")

    print(speed_cmd)
    print(move)
    print(turn)
    print(enable)

    #edition des commandes de mouvement
    if ~move:
        cmd_mv = (50 + move*speed_cmd) & ~0x80
    else:
        cmd_mv = (50 + move*speed_cmd) | 0x80

    if ~turn:
        cmd_turn = 50 +turn*20 & 0x80
    else:
        cmd_turn = 50 + turn*20 | 0x80

    print(" mv:",cmd_mv," turn:",cmd_turn)
    '''
    #if not cmd: continue
    print('val cmd : ',cmd)
    head, data = cmd.split(':')
    print('head : ', head, ' data : ', data)
    
    #print('head : ', data[0], ' data : ', data[1])
    '''
