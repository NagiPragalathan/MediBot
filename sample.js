let count=0;
console.log("working..");
function change_date(){
  console.log("clicked..");
  let obj = document.getElementById('demo');
  if(count%2==0){
    obj.innerHTML = Date();
  }else{
    obj.innerHTML = "Click the button to show the Date";
  }
  count++;
}
