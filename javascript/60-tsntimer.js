/*
var banner_mode = 0;
var default_text = '<a href="/live/">Прямой эфир</a> каждый четверг в 21:00 МСК';

function somefunction(){

	if (banner_mode==0) {
			currDate = new Date(); //узнаем текущую дату
			TZOffset=-1*(currDate.getTimezoneOffset()+4*60);
			//вычисляем сколько минут должно пройти с начала недели до ТСН по Москве
			var TSNMinutes=4*24*60+21*60+TZOffset; //с поправкой на часовой пояс
			var WeekMinutes=7*24*60; //минут в неделе
			var weekDay=currDate.getDay(); //порядковый номер дня недели
			var hours=currDate.getHours(); //час
			var minutes=currDate.getMinutes(); //минута

			var CurrMinutes=weekDay*24*60+hours*60+minutes; //сколько у нас прошло минут с начала недели
			var dMinutes=TSNMinutes-CurrMinutes; //разница в минутах
			if (dMinutes<0) dMinutes+=WeekMinutes; //если ТСН на этой неделе уже прошел
			var lDays=Math.floor(dMinutes/(24*60)) //осталось дней
			var lHours=Math.floor((dMinutes-lDays*24*60)/60); //осталось часов
			var lMinutes=dMinutes-lDays*24*60-lHours*60; //осталось минут
			//шаманство с окончаниями
			if (lDays==0) var dayStr='';
			if (lDays==1) var dayStr='1&nbsp;день';
			if (lDays==2 || lDays==3 || lDays==4) var dayStr=lDays+'&nbsp;дня';
			if (lDays>4) var dayStr=lDays+'&nbsp;дней';
			
			if (lHours==0) var hourStr='';
			if (lHours==1) var hourStr='1&nbsp;час';
			if (lHours==2 || lHours==3 || lHours==4 || lHours==22 || lHours==23 || lHours==24) 
				var hourStr=lHours+'&nbsp;часа';
			if (lHours>4 && lHours<=20) var hourStr=lHours+'&nbsp;часов';
			if (lHours==21) var hourStr=lHours+'&nbsp;час';
			
			minStr=lMinutes+'&nbsp;минут';
			if (lMinutes==0) var minStr='ровно';
			lMinutes_=lMinutes%10
			if (lMinutes_==1) var minStr=lMinutes+'&nbsp;минута';
			if (lMinutes_==2 || lMinutes_==3 || lMinutes_==4) var minStr=lMinutes+'&nbsp;минуты';
			if (lMinutes>9 && lMinutes<21) var minStr=lMinutes+'&nbsp;минут';
			//начинаем составлять результат
			var result='';
			if (dayStr!='') result+=dayStr+', ';
			if (hourStr!='') result+=hourStr+', ';
			result+=minStr;
			result+=' до <a href="/live/">прямого эфира</a>';
			//если эфир уже идет, результат должен быть другой
			if (lDays==0 && lHours==0 && lMinutes==0) result='<a href="/live/">Прямой эфир</a> начался!';
			if (lDays==6 && lHours==23) result='<a href="/live/">Прямой эфир</a> прямо сейчас!';
			if (lDays==6 && lHours==22) result='<a href="/live/">Прямой эфир</a> ещё идет!';
			//заносим результат на баннер
			document.getElementById('timerBanner').innerHTML=result;
			//меняем режим
			banner_mode = 1;
		} else if (banner_mode==1) {
			//ставим обратно начальный текст
			document.getElementById('timerBanner').innerHTML=default_text;
			banner_mode = 0;
		}; 	
	};

// стартуем периодическую смену баннера
timerUpdate = window.setInterval(somefunction, 5000)
*/
