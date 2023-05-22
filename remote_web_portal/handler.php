<?php
$password="password";

$choices=array("l1","l2","f1");

if(isset($_GET['action'])){$action=$_GET['action'];}
else{$action="";}

if (in_array($action,$choices)){
    
    try{
        
    $data=json_decode(stripslashes(file_get_contents("php://input")),true);
    if(!(isset($data['password']) and $data['password']==$password)){//wrong password/no password
        echo json_encode(["res"=>1]);
        exit();
    }
    
    try{    $status=fgets(fopen($action,'r'));  }
    catch(Exception $e){$status="1";}
    
    $file=fopen(strval($action),'w');
    if ($status=="0"){fwrite($file,"1");}
    else{fwrite($file,"0");}
    
    fclose($file);
    }
    catch(Exception $e){
        echo json_encode(["res"=>0]);
    }
    echo json_encode(["res"=>1]);
}
else if($action=='get'){
    try{
    $res=array();
    foreach ($choices as $choice){
        $file=fopen($choice,'r');
        $res[$choice]=fgets($file);
    }
    
    }
    catch(Exception $e){
       
       echo 0;
    }    
    $vals=array_values($res);
    $res_str="";
    for($i=0;$i<count($vals);$i++){
        $res_str= $res_str.$vals[$i];
    }
    echo $res_str;
}
else if($action=='ip'){
    $file=fopen("ip","r");
    $ip=fgets($file);
    fclose($file);
    echo $ip;
    exit();
}
else{
    echo 3;
}
?>
