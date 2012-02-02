tmradio = {
	/**
	 * Inline MP3 player template.  URL will be placed instead of "FILE_URL".
	 */
	player_template: '<object classid="clsid:D27CDB6E-AE6D-11cf-96B8-444553540000" codebase="http://download.macromedia.com/pub/shockwave/cabs/flash/swflash.cab#version=10,0,0,0" width="15" height="15"><param name="movie" value="http://www.strangecube.com/audioplay/online/audioplay.swf?file=FILE_URL&amp;auto=yes&amp;sendstop=yes&amp;repeat=1&amp;buttondir=http://www.strangecube.com/audioplay/online/alpha_buttons/negative_small&amp;bgcolor=0xffffff&amp;mode=playpause"><param name="quality" value="high"/><param name="wmode" value="transparent"/><embed src="http://www.strangecube.com/audioplay/online/audioplay.swf?file=FILE_URL&amp;auto=yes&amp;sendstop=yes&amp;repeat=1&amp;buttondir=http://www.strangecube.com/audioplay/online/alpha_buttons/negative_small&amp;bgcolor=0xffffff&amp;mode=playpause" quality="high" wmode="transparent" width="15" height="15" align="" type="application/x-shockwave-flash" pluginspage="http://www.macromedia.com/go/getflashplayer"></embed></object>',

	pagelist: {
		/**
		 * Installs event handlers.
		 */
		ready: function () {
			$("table.pagelist .play a").click(tmradio.pagelist.play);
		},

		/**
		 * Replaces the clicked PLAY icon with an SWF player (in auto-start mode).
		 */
		play: function () {
			var url = $(this).attr("href");
			var html = tmradio.player_template
				.replace("FILE_URL", url)
				.replace("FILE_URL", url);
			$(this).parent().html(html);
			return false;
		}
	}
};
