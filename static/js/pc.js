const messagesContainer = document.getElementById('messages');
const input = document.getElementById('input');
const sendButton = document.getElementById('send');
var qaIdx = 0,answers={},answerContent='',answerWords=[];
var codeStart=false,lastWord='',lastLastWord='';
var typingTimer=null,typing=false,typingIdx=0,contentIdx=0,contentEnd=false;

//markdown解析，代码高亮设置
marked.setOptions({
    highlight: function (code, language) {
        const validLanguage = hljs.getLanguage(language) ? language : 'javascript';
        return hljs.highlight(code, { language: validLanguage }).value;
    },
});

//在输入时和获取焦点后自动调整输入框高度
input.addEventListener('input', adjustInputHeight);
input.addEventListener('focus', adjustInputHeight);

// 自动调整输入框高度
function adjustInputHeight() {
    input.style.height = 'auto'; // 将高度重置为 auto
    input.style.height = (input.scrollHeight+2) + 'px';
}

//按下回车健直接发送消息
function btn_onkeypress(e) {
    if(e.keyCode ==13){
        sendMessage();
    }
}

function sendMessage() {
    const inputValue = input.value;
    if (!inputValue) {
        alert('请输入提问！');
        return;
    }

    const question = document.createElement('div');
    question.setAttribute('class', 'message question');
    question.setAttribute('id', 'question-'+qaIdx);
    question.innerHTML = marked.parse(inputValue);
    messagesContainer.appendChild(question);

    const answer = document.createElement('div');
    answer.setAttribute('class', 'message answer');
    answer.setAttribute('id', 'answer-'+qaIdx);
    messagesContainer.appendChild(answer);
    answers[qaIdx] = document.getElementById('answer-'+qaIdx);

    input.value = '';
    input.disabled = true;
    sendButton.disabled = true;
    adjustInputHeight();

    typingTimer = setInterval(typingWords, 50);
    const subStr = inputValue.substring(0, 5).toLowerCase().trim(); 
    // console.log("subStr:"+subStr);

    switch(subStr){
        case "/img":
            answer.innerHTML = marked.parse('小A制图较慢，请耐心等待…');
            getImage(inputValue);
            break
        case "/tts":
            answer.innerHTML = marked.parse('小A语音生成中……');
            getVoice(inputValue);
            break
        case "/gpt4":
            answer.innerHTML = marked.parse('來自gpt4的回答');
            subStr_after = inputValue.slice(5).trim();
            getAnswer(subStr_after,'gpt4');
            break
        case "/wxyy":
            answer.innerHTML = marked.parse('文心一言說:');
            subStr_after = inputValue.slice(5).trim();
            getAnswer(subStr_after,'wxyy');
            break
        default:
            answer.innerHTML = marked.parse('小A思考中……');
            getAnswer(inputValue);
    }
    // if(subStr=="/img"){
    //     answer.innerHTML = marked.parse('小A制图较慢，请耐心等待…');
    //     getImage(inputValue);
    // }else{
    //     answer.innerHTML = marked.parse('小A思考中……');
    //     getAnswer(inputValue);
    // }
}
function getImage(inputValue){
    modelName = sendButton.getAttribute("data-m")
    inputValue = encodeURIComponent(inputValue.replace(/\+/g, '{[$add$]}'));
    const url = "img?m="+ modelName +"&q="+inputValue;

    var xhr = new XMLHttpRequest(); // 创建新的XHR对象
    xhr.open('POST', url); // 设置请求类型和URL
    xhr.onreadystatechange = function() { // 定义状态改变时的处理函数
        if (xhr.readyState === 4 && xhr.status === 200) { // 当请求完成且返回正常结果时
            var responseData = JSON.parse(xhr.responseText); // 将响应文本转换为JSON格式
            img_content="<div><img src='gpt/show?image="+ responseData.imageurl +"' /></div>";
            // console.log('img_content:'+img_content); // 输出响应数据到控制台

            answerWords.push(img_content);
            contentIdx += 1;
            contentEnd = true;
            input.disabled = false;
            sendButton.disabled = false;
        }
    };
    xhr.send(); // 发送请求
}
function getVoice(inputValue){
    inputValue = encodeURIComponent(inputValue.replace(/\+/g, '{[$add$]}'));
}


function getAnswer(inputValue,modelName='gpt'){
    // modelName = sendButton.getAttribute("data-m");
    inputValue = encodeURIComponent(inputValue.replace(/\+/g, '{[$add$]}'));
    //var url="";
    
    let url = "chat?m="+ modelName +"&q="+inputValue;
    if (modelName=='wxyy'){
        url = "wxyy/stream?m="+ modelName +"&q="+inputValue;
    }
    console.log('url:',url);
    const eventSource = new EventSource(url);

    eventSource.addEventListener("open", (event) => {
        console.log("连接已建立", JSON.stringify(event));
    });

    eventSource.addEventListener("message", (event) => {
        console.log("接收数据：", event.data);
        try {
            if (event.data == "[done]" || event.data == undefined){
                //console.log("[done]:"+event.data);
                eventSource.close();
                contentEnd=true;
                
                input.disabled = false;
                sendButton.disabled = false;
            }
            else{
                answerWords.push(event.data);
                contentIdx += 1;
            }
        } catch (error) {
            console.log(error);
            eventSource.close();
        }
    });

    eventSource.addEventListener("error", (event) => {
        eventSource.close();
        console.error("发生错误：", JSON.stringify(event));
    });

    eventSource.addEventListener("close", (event) => {
        console.log("连接已关闭", JSON.stringify(event.data));
        eventSource.close();
        contentEnd = true;
        console.log((new Date().getTime()), 'answer end');
    });
}

function typingWords(){
    if(contentEnd && contentIdx==typingIdx){
        clearInterval(typingTimer);
        answerContent = '';
        answerWords = [];
        answers = [];
        qaIdx += 1;
        typingIdx = 0;
        contentIdx = 0;
        contentEnd = false;
        lastWord = '';
        lastLastWord = '';
        input.disabled = false;
        sendButton.disabled = false;
        // console.log((new Date().getTime()), 'typing end');
        return;
    }
    if(contentIdx<=typingIdx){
        return;
    }
    if(typing){
        return;
    }
    typing = true;

    if(!answers[qaIdx]){
        answers[qaIdx] = document.getElementById('answer-'+qaIdx);
    }

    const content = answerWords[typingIdx];
    if(content.indexOf('`') != -1){
        if(content.indexOf('```') != -1){
            codeStart = !codeStart;
        }else if(content.indexOf('``') != -1 && (lastWord + content).indexOf('```') != -1){
            codeStart = !codeStart;
        }else if(content.indexOf('`') != -1 && (lastLastWord + lastWord + content).indexOf('```') != -1){
            codeStart = !codeStart;
        }
    }

    lastLastWord = lastWord;
    lastWord = content;

    answerContent += content;
    answers[qaIdx].innerHTML = marked.parse(answerContent+(codeStart?'\n\n```':''));

    typingIdx += 1;
    typing = false;
}
