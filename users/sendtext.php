<?php

$auth_token = '4bd273d26767de65-b3ec3ba4114fb6af-16ad4821f728c913';
$send_name = "napominalkka_bot";

function sendReq($data)
{
    $request_data=json_encode($data);

    $ch=curl_init("https://chatapi.viber.com/pa/send_message");
    curl_setopt($ch, CURLOPT_POST, 1);
    curl_setopt($ch, CURLOPT_POSTFIELDS, $request_data);
    curl_setopt($ch, CURLOPT_HTTPHEADER, array('Content-Type: application/json'));
    $response = curl_exec($ch);
    $err = curl_error($ch);
    curl_close($ch);
    if($err) {return $err;}
    else {return $response;}
}

function sendMsg($sender_id, $text, $type, $tracking_data=Null, $arr_asoc=Null)
{
    global $auth_token, $send_name;

    $data['auth_token']=$auth_token;
    $data['receiver']=$sender_id;
    if($text != Null) {$data['text']=$text;}
    $data['type']=$type;
    $data['sender']['name']=$send_name;
    if($tracking_data != Null) {$data['tracking_data']=$tracking_data;}
    if ($arr_asoc != Null)
    {
        foreach($arr_asoc as $key => $val) {$data[$key]=$val;}
    }

    return sendReq($data);
}

function sendMsgText($sender_id, $text, $tracking_data=Null)
{
    return sendMsg($sender_id, $text, "text", $tracking_data);
}

$sender_id = $argv[1];
$index = $argv[2];
$text = $argv[3];
echo $index;

$just_string = '';
$i = 2;
foreach($argv as $num){
   $just_string .= ' ' . $num;
}

echo $text;
// $cut_param = strlen($text)-35;
//$response_text = substr($text, $cut_param);
// echo count($text);
// $text2=implode(", ", $arr)
echo gettype($text);
echo gettype($just_string);
sendMsgText($sender_id, substr($just_string, 78));

?>
