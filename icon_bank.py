import re


def clean_text(text):
    return re.sub('\\W+', '', text).lower()


icon_bank = {
    'akinosaren': '<:akinosaren:1166119060514291823>',
    'akarin': '<:AKarin:1166116613100163182>',
    'ameth': '<:Ameth:1166088273727344761>',
    'ayori': '<:AYori:1166121461463908512>',
    'christina': '<:Christina:1166116614484271305>',
    'cayukari': '<:CAYukari:1166121462504108143>',
    'cillya': '<:CIlya:1166116616698855514>',
    'creditta': '<:Creditta:1166095536366030849>',
    'croche': '<:Croche:1166104808269287454>',
    'ctamaki': '<:CTamaki:1166095538169577602>',
    'cyukari': '<:CYukari:1168051732127957063>',
    'djeeta': '<:Djeeta:1166116618049441873>',
    'eayane': '<:EAyane:1166116619781681172>',
    'emaho': '<:EMaho:1166121464341200961>',
    'fprecia': '<:FPrecia:1177426913216708730>',
    'fquria': '<:FQuria:1177426914160422983>',
    'friri': '<:FRiri:1177426915926224936>',
    'homare': '<:Homare:1166121466677448714>',
    'htomo': '<:HTomo:1166116621325176984>',
    'karin': '<:Karin:1166116622893842502>',
    'labyrista': '<:Labyrista:1166095540023480350>',
    'lmuimi': '<:LMuimi:1166104813814157362>',
    'lnozomi': '<:LNozomi:1166104815366058094>',
    'lyrael': '<:Lyrael:1166116624840007710>',
    'makoto': '<:Makoto:1166116626274459670>',
    'mgmonika': '<:MGMonika:1166121468363550842>',
    'misora': '<:Misora:1166466395958153226>',
    'monika': '<:Monika:1166104817438031914>',
    'muimi': '<:Muimi:1166104819379994644>',
    'neneka': '<:Neneka:1166104821393281124>',
    'nkuuka': '<:NKuuka:1166116629617319966>',
    'nyhomare': '<:NYHomare:1166104824727744563>',
    'nymisato': '<:NYMisato:1166104826774573056>',
    'nyneneka': '<:NYNeneka:1166105046459629699>',
    'nyshefi': '<:NYShefi:1166116631710273616>',
    'olpecorine': '<:OLPecorine:1166116662869774356>',
    'oyuki': '<:OYuki:1166116635724226691>',
    'phiyori': '<:PHiyori:1168051401360941087>',
    'pianna': '<:PIAnna:1166119061827096729>',
    'pkokkoro': '<:PKokkoro:1166119064096219236>',
    'pkyaru': '<:PKyaru:1166116673460383754>',
    'prei': '<:PRei:1166121469651210261>',
    'ranpha': '<:Ranpha:1177426917067071668>',
    'rshiori': '<:RShiori:1177426918073704468>',
    'sakino': '<:SAkino:1166104829458915399>',
    'saruka': '<:SaRuka:1166466397241622648>',
    'sasaren': '<:SaSaren:1166466399129063546>',
    'schika': '<:SChika:1166106847195955250>',
    'sfyuni': '<:SFYuni:1166116690489262131> ',
    'shefi': '<:Shefi:1166116691936292904>',
    'shiori': '<:Shiori:1177426920065994804>',
    'skokkoro': '<:SKokkoro:1166095541885747241>',
    'smimi': '<:SMimi:1166105221982847089>',
    'sneneka': '<:SNeneka:1166104834961834034>',
    'snozomi': '<:SNozomi:1166116694431907982>',
    'sranpha': '<:SRanpha:1166104837285478551>',
    'srei': '<:SRei:1166116697162395699>',
    'ssaren': '<:SSaren:1166466401003900998>',
    'sshinobu': '<:SShinobu:1166116698848514128>',
    'ssuzume': '<:SSuzume:1166105290467459194>',
    'stamaki': '<:STamaki:1166466403554054174>',
    'stkurumi': '<:STKurumi:1166116701532860586>',
    'syui': '<:SYui:1166121471085658282>',
    'syukari': '<:SYukari:1166105259421208709>',
    'tamaki': '<:Tamaki:1166466404908793856>',
    'tomo': '<:Tomo:1166116702929567784>',
    'tskyaru': '<:TSKyaru:1166116704116555817>',
    'tssuzuna': '<:TSSuzuna:1177426921148133467>',
    'vampy': '<:Vampy:1166121473065365596>',
    'vikala': '<:Vikala:1166116705962033173>',
    'wdjeeta': '<:WDjeeta:1166116707564269648>',
    'wmatsuri': '<:WMatsuri:1166121474290098206>',
    'xakari': '<:XAkari:1168051403529396265>',
    'xmiyako': '<:XMiyako:1166121475519037490>',
    'xjun': '<:XJun:1166116708835147859>',
    'xyori': '<:XYori:1166116711955701790>',
    'xyukari': '<:XYukari:1166542269415952475>',

    'greeno': '<:greeno:1168060002636935168>'
}
