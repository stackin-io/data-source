
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html lang="pt-br" xmlns="http://www.w3.org/1999/xhtml">
<head><title>
	Portal da Nota Fiscal Eletrônica
</title>

    <!-- CSS -->
    <link href="css/geral.css" rel="stylesheet" type="text/css" /><link href="css/classes.css" rel="stylesheet" type="text/css" /><link href="css/paginasInternas.css" rel="stylesheet" type="text/css" /><link href="css/estilo_visualizacao.css" rel="stylesheet" type="text/css" />

	
    <!-- Javascript -->
    <script src="scripts/jquery-3.2.1.min.js" type="text/javascript"></script>
    <script src="scripts/menu.js" type="text/javascript"></script>
    <script src="scripts/mascaras.js" type="text/javascript"></script>
    <script src="//www.receita.fazenda.gov.br/estatistica/estatistica.js" type="text/javascript"></script>
    <script src="scripts/captcha-som.js" type="text/javascript"></script>

    <meta http-equiv="cache-control" content="no-store, no-cache, must-revalidate, Post-Check=0, Pre-Check=0" /><meta http-equiv="pragma" content="no-cache" /><meta http-equiv="expires" content="0" />

    <script type="text/javascript">
        document.addEventListener('keydown', function (e) {
            if (e.ctrlKey && e.shiftKey && e.code === 'KeyQ') {
                var popup = document.getElementById('ctl00_PanelPopup');
            popup.style.display = popup.style.display === 'none' ? 'block' : 'none';
        }
    });
    </script>



    
</head>
<body onselectstart="return true;">
    <div id="barra-brasil" style="background: #7F7F7F; height: 20px; padding: 0 0 0 10px; display: block;">
        <ul id="menu-barra-temp" style="list-style: none;">
            <li style="display: inline; float: left; padding-right: 10px; margin-right: 10px; border-right: 1px solid #EDEDED">
                <a href="http://brasil.gov.br" style="font-family: sans,sans-serif; text-decoration: none; color: white;">Portal do Governo Brasileiro</a></li>
            <li><a style="font-family: sans,sans-serif; text-decoration: none; color: white;" href="http://epwg.governoeletronico.gov.br/barra/atualize.html">Atualize sua Barra de Governo</a></li>
        </ul>
    </div>
   
    <script defer="defer" src="//barra.brasil.gov.br/barra.js" type="text/javascript"></script>
 


    <div id="divCentral">
        <form method="post" action="./download.aspx?tipoConteudo=vBO%2f4eBj5F4%3d" id="aspnetForm">
<div class="aspNetHidden">
<input type="hidden" name="__EVENTTARGET" id="__EVENTTARGET" value="" />
<input type="hidden" name="__EVENTARGUMENT" id="__EVENTARGUMENT" value="" />
<input type="hidden" name="__VIEWSTATE" id="__VIEWSTATE" value="/wEPDwUKLTU4NDEyNTAzNw9kFgJmD2QWAgIDD2QWEAILDw8WAh4EVGV4dAUQMzY0LDg1MyBtaWxow7Vlc2RkAg8PDxYCHwAFCjQyLDI5MyBtaWxkZAIRDw8WAh4LTmF2aWdhdGVVcmwFFWluZm9Fc3RhdGlzdGljYXMuYXNweGRkAhUPDxYCHwEFRWh0dHBzOi8vaG9tLm5mZS5mYXplbmRhLmdvdi5ici9hcmVhcmVzdHJpdGEvaW5pY2lhbC9hdXRlbnRpY2FjYW8uYXNweGRkAhkPDxYCHwEFMnBlcmd1bnRhc0ZyZXF1ZW50ZXMuYXNweD90aXBvQ29udGV1ZG89M093MW5mVEJ6SW89ZGQCKQ88KwARAwAPFgQeC18hRGF0YUJvdW5kZx4LXyFJdGVtQ291bnQCBWQBEBYAFgAWAAwUKwAAFgJmD2QWDmYPDxYCHgdWaXNpYmxlaGRkAgEPZBYCZg9kFgICAQ8PFgYeDUFsdGVybmF0ZVRleHQFK01hbmlmZXN0byBFbGV0csO0bmljbyBkZSBEb2N1bWVudG9zIEZpc2NhaXMeD0NvbW1hbmRBcmd1bWVudAUuaHR0cHM6Ly9kZmUtcG9ydGFsLnNlZmF6dmlydHVhbC5ycy5nb3YuYnIvTURGZR4ISW1hZ2VVcmwFHX4vaW1hZ2Vucy9iYW5uZXJfbWRmZV9PZmYucG5nFgIeBXRpdGxlBStNYW5pZmVzdG8gRWxldHLDtG5pY28gZGUgRG9jdW1lbnRvcyBGaXNjYWlzZAICD2QWAmYPZBYCAgEPDxYGHwUFJkNvbmhlY2ltZW50byBkZSBUcmFuc3BvcnRlIEVsZXRyw7RuaWNvHwYFHWh0dHA6Ly93d3cuY3RlLmZhemVuZGEuZ292LmJyHwcFJH4vaW1hZ2Vucy9iYW5uZXJzX1Zpc2l0ZV9DVGVfT2ZmLnBuZxYCHwgFJkNvbmhlY2ltZW50byBkZSBUcmFuc3BvcnRlIEVsZXRyw7RuaWNvZAIDD2QWAmYPZBYCAgEPDxYGHwUFKVNpc3RlbWEgUMO6YmxpY28gZGUgRXNjcml0dXJhw6fDo28gRmlzY2FsHwYFI2h0dHA6Ly93d3cxLnJlY2VpdGEuZmF6ZW5kYS5nb3YuYnIvHwcFJX4vaW1hZ2Vucy9iYW5uZXJzX1Zpc2l0ZV9TcGVkX09mZi5wbmcWAh8IBSlTaXN0ZW1hIFDDumJsaWNvIGRlIEVzY3JpdHVyYcOnw6NvIEZpc2NhbGQCBA9kFgJmD2QWAgIBDw8WBh8FBSpTdXBlcmludGVuZMOqbmNpYSBkYSBab25hIEZyYW5jYSBkZSBNYW5hdXMfBgUaaHR0cDovL3d3dy5zdWZyYW1hLmdvdi5ici8fBwUgfi9pbWFnZW5zL2Jhbm5lcnNfbWFuYXVzX09mZi5wbmcWAh8IBSpTdXBlcmludGVuZMOqbmNpYSBkYSBab25hIEZyYW5jYSBkZSBNYW5hdXNkAgUPZBYCZg9kFgICAQ8PFgYfBQUyUG9ydGFsIE5hY2lvbmFsIGRvIEJpbGhldGUgZGUgUGFzc2FnZW0gRWxldHLDtG5pY28fBgUtaHR0cHM6Ly9kZmUtcG9ydGFsLnNlZmF6dmlydHVhbC5ycy5nb3YuYnIvQlBlHwcFHH4vaW1hZ2Vucy9iYW5uZXJfYnBlX09mZi5wbmcWAh8IBTJQb3J0YWwgTmFjaW9uYWwgZG8gQmlsaGV0ZSBkZSBQYXNzYWdlbSBFbGV0csO0bmljb2QCBg8PFgIfBGhkZAI5Dw8WAh8ABTdQb3J0YWwgZGEgTkYtZSAyMDI2IC0gTm90YSBGaXNjYWwgRWxldHLDtG5pY2EgIHYyLjkuOS4wZGQCOw8PFgIfAAUZQW1iaWVudGUgZGUgSG9tb2xvZ2HDp8Ojb2RkGAIFHl9fQ29udHJvbHNSZXF1aXJlUG9zdEJhY2tLZXlfXxYGBQ9jdGwwMCRpYnRCdXNjYXIFKWN0bDAwJGdkdkxpbmtzRGVzdGFxdWUkY3RsMDIkSW1hZ2VCdXR0b24xBSljdGwwMCRnZHZMaW5rc0Rlc3RhcXVlJGN0bDAzJEltYWdlQnV0dG9uMQUpY3RsMDAkZ2R2TGlua3NEZXN0YXF1ZSRjdGwwNCRJbWFnZUJ1dHRvbjEFKWN0bDAwJGdkdkxpbmtzRGVzdGFxdWUkY3RsMDUkSW1hZ2VCdXR0b24xBSljdGwwMCRnZHZMaW5rc0Rlc3RhcXVlJGN0bDA2JEltYWdlQnV0dG9uMQUWY3RsMDAkZ2R2TGlua3NEZXN0YXF1ZQ88KwAMAQgCAWTOiFumJLoxSlPjPZZOQzuUOfEdpw==" />
</div>

<script type="text/javascript">
//<![CDATA[
var theForm = document.forms['aspnetForm'];
if (!theForm) {
    theForm = document.aspnetForm;
}
function __doPostBack(eventTarget, eventArgument) {
    if (!theForm.onsubmit || (theForm.onsubmit() != false)) {
        theForm.__EVENTTARGET.value = eventTarget;
        theForm.__EVENTARGUMENT.value = eventArgument;
        theForm.submit();
    }
}
//]]>
</script>


<script src="/Portal/WebResource.axd?d=ZWO9axJrMUCOr1izP3UEZRCC9H9dses7etW7JecjiAOQDqMwdG-StzfDPAgcsQ8hxRkl-AMsAJBR-BfkCGB56pQ3gKo1&amp;t=639190725332169432" type="text/javascript"></script>


<script src="/Portal/ScriptResource.axd?d=mEdZQL4-NwECxt-JTyttk6L9nZIgV2gXEYVXAtZsi0K6ekMkFlv9Yn_Kj22VMi8DGrNLu0_DpTP9BqO8cJwvdqgjvvPW2azeebt459xHltLpU2IYCjWzfsXnSvCpl58N24rAFBpwmeIv8vlDIdkuJMLyc185M28vUneHfEZinqa8QFoa0&amp;t=ffffffffbec1863d" type="text/javascript"></script>
<script src="/Portal/ScriptResource.axd?d=_4eicGuFpUqdgWen_lV3HusxGEZOmOKKDBxJqwShbSOkmNnRzePJCRrfaqi4yAG4omXSLCzZIOXtktjVsEiYo-GKVvPgshIWEGRj0wBWGGBZ17M9NOTmgil71sUoZPjju8MLRc_ZAKcMsgCu1bH4TYQkMzdgF4kGwmOy40aQpegCvFgb0&amp;t=ffffffffbec1863d" type="text/javascript"></script>
<script src="/Portal/ScriptResource.axd?d=mT0y51o0LUqDERR1gK1PHgdY4dmheOGIEDsXTAvO15rluXxRmlDpbs2OZ5GzabS8ogN435zUFAzSJzOrMm273LNi9kZaBmfIr0PVpeY4-vWwhlIQYTGcvGdpKZHGke6lc6yRzn6USQ_EFxLZL1yRaRizerg1&amp;t=ffffffff87636c38" type="text/javascript"></script>
<script src="/Portal/ScriptResource.axd?d=mNl4X5z8gakgoLeSKYyjidGXzDI8WB_js4c1BOO0SSuYnxrESMP3UuYxSNorl1bu2ullLNpjhtJZfqvuPfq8VIKxbhTYLUh7VwLGXDUL71x3QnCVhGvW8Jj_VC2_LMItPVyX2fC6DCfiCRENC9-saVW3pew1&amp;t=ffffffff87636c38" type="text/javascript"></script>
<script src="/Portal/ScriptResource.axd?d=gy1cG5fQPk2O5gMbY0Pn3yHuPzFtfmg8QV1Pogc1KBWIteuUKmKBuBIyfW6KqHWIvgFeCm3oM-z5WZSRNugLOVc55rLnYVeKyHRamgeBETeIpLo0gpVt7LFGQ7bKUNRono7LVxGw777PGlSFHyqC91m3kP41&amp;t=ffffffff87636c38" type="text/javascript"></script>
<script src="/Portal/ScriptResource.axd?d=aNMBzIixTOb4x9OTZNL5biKT0bpsWTKFMlit8dMFQJavlF2hvLsk_Wlk0VVmlETfWHY1ZX0PZI0HRrl3Cs8XWmJdvPuGfmYNTUTC_ZUO6a3_BTOOTWwfHEmr5YKwWwIY9Q4muUyNtv1eMDjmNJMtC4OMSCtFzSfY1oTKlV65AYDShHn90&amp;t=ffffffff87636c38" type="text/javascript"></script>
<script src="/Portal/ScriptResource.axd?d=hrh3Yb6czhWN6wUcMZcUIeFOLf8grYBT6HRxG1BYQae0SChobBeHW4T_zIJTyIaQOnDjcTFfQhYdP19zBElCxyRv6CmBwEPXAAdjHE2nI6VmTzhLMs638WBFuAYwkLSf8lHbIF1OX750GX0TLea66fbTLEg2XV3OrgeL_2WtW-YygiYH0&amp;t=ffffffff87636c38" type="text/javascript"></script>
<script src="/Portal/ScriptResource.axd?d=vz8B9u4YtVYX1pVqKcPnTT5VAHjqfY7XelyFKI4TdQTifTuY9dnz1e811Kfd2J734nTtqNu1JVebhTGlFncJMGmkBtDc3CnuIQD99rtw0doLzeqZwljjDwrsd35OJb4v96jNLff34pUPIDT3edHBA3bRPj_SlcRScFLyjafLvlBejTK-0&amp;t=ffffffff87636c38" type="text/javascript"></script>
<script src="/Portal/ScriptResource.axd?d=u9gFRG_7YktrV4NulEFzs0AbMrx8VSF73ldTY0YL-OuOO1zkEapDJywAv1vyYUGySV1TRiwVILUTmCcRQFqF-cfvgxFpRh9zMy3JMh90gP-KyJUT75SzPtk-LwlXSmNqp5_lXIOKCcldvFCOMY_4HY9xoVWKkN5p6PeL-R8PvJ6xw0xL0&amp;t=ffffffff87636c38" type="text/javascript"></script>
<div class="aspNetHidden">

	<input type="hidden" name="__VIEWSTATEGENERATOR" id="__VIEWSTATEGENERATOR" value="2FE0FE5F" />
	<input type="hidden" name="__EVENTVALIDATION" id="__EVENTVALIDATION" value="/wEdAApqvC34vlwu2FNrnccOutWsZLQlHz+zjyg7L4aHZvZX1VRXlc/8UyQ3XSUj7QL9zmMEao+HCuWf709Mb5rjbkLgNCckUz+Zyz93RVMykxNgIZ447S1NfnWN7VA5SBuEBeJOjU6XyL6ErgbhWj6OwNA5jxoQlmOeg+bJl0yPRxMOmzTZNOtTvRyGaT6hhlTIEUNN11GISA+gOcqDGnwa1tFKyu3QMyNXYd4mHrUhOjhYtbjVEqY=" />
</div>
            <script type="text/javascript">
//<![CDATA[
Sys.WebForms.PageRequestManager._initialize('ctl00$ScriptManager', 'aspnetForm', ['tctl00$upnBuscar',''], [], [], 90, 'ctl00');
//]]>
</script>


            <div id="ctl00_PanelPopup" style="display: none; position: fixed; top: 50%; left: 50%; transform: translate(-50%, -50%); z-index: 100; background-color: white; padding: 20px; border: 1px solid #ccc; box-shadow: 0px 0px 10px #ccc;">
	
                <span id="ctl00_LabelPopup">Deseja acessar a Área Restrita com autenticação via GovBR?</span>
                <br />
                <br />
                <input type="submit" name="ctl00$ButtonAcessar" value="Acessar" onclick="window.location=&#39;https://hom.nfe.fazenda.gov.br/arearestrita/inicial/autenticacao.aspx&#39;; return false;" id="ctl00_ButtonAcessar" />
                &nbsp;
            <input type="submit" name="ctl00$ButtonSair" value="Sair" onclick="document.getElementById(&#39;&lt;%= PanelPopup.ClientID %>&#39;).style.display=&#39;none&#39;; return false;" id="ctl00_ButtonSair" />

            
</div>

            <div id="tudoSemRodape" class="contemFloat">
                <div id="cabecalho">
                    <div id="menuAcessibilidade">
                        <?xml version="1.0" encoding="utf-8"?><a href="listaSubMenu.aspx?Id=6H4uVlIEaKs=">Conheça a NF-e</a><a href="listaSubMenu.aspx?Id=esCrSQFUvGg=">Serviços</a><a href="listaSubMenu.aspx?Id=ndIjl+iEFdE=">Legislação</a><a href="listaSubMenu.aspx?Id=04BIflQt1aY=">Documentos</a><a href="listaSubMenu.aspx?Id=BMPFMBoln3w=">Downloads</a><a href="https://hom.nfe.fazenda.gov.br/arearestrita/inicial/autenticacao.aspx">Área Restrita</a><a href="https://hom.nfe.fazenda.gov.br/arearestrita/inicial/listaSubMenu.aspx?Id=UORZ3ynALMA=">Documentos e outros</a><a href="listaSubMenu.aspx?Id=VOYEgBgD3iU=">Outros DF-e</a>
                    </div>
                    
                    <div id="divTransparente" onclick="javascript:location.href = 'principal.aspx'">
                    </div>
                    <div id="imgHome">
                        <a href="principal.aspx">
                            <img id="ibtHome" src="imagens/home_icon_Off.png" onmouseover="javascript: trocarImagem(this)"
                                onmouseout="javascript: trocarImagem(this)" alt="Link para a página inicial do Portal da NF-e" />
                        </a>
                    </div>
                    <div id="menu">
                        <?xml version="1.0" encoding="utf-8"?><ul class="abasMenu" xmlns:chave="http://exslt.org/chaveacesso"><li class="itemMenuPrincipal"><a href="listaSubMenu.aspx?Id=esCrSQFUvGg=">Serviços</a><ul class="dropdown"><li><a href="consultaRecaptcha.aspx?tipoConsulta=resumo&amp;tipoConteudo=7PhJ+gAVw2g=">Consultar NF-e</a></li><li><a href="consulta.aspx?tipoConsulta=inutilizacao&amp;tipoConteudo=nDmpH/MjKrg=">Consultar Inutilização</a></li><li><a href="solicitaCertificado.aspx?tipoConteudo=kxzTbaUQE+4=">Consultar Duplicidade AN</a></li><li><a href="consulta.aspx?tipoConsulta=duplicidade&amp;tipoConteudo=JryDMXCxwtM=">Consultar Duplicidade SVC</a></li><li><a href=" disponibilidade.aspx?versao=0.00&amp;tipoConteudo=P2c98tUpxrI=">Consultar Disponibilidade</a></li><li><a href="manifestacaoDestinatario.aspx?tipoConteudo=BS6VqmEd2vM=">Manifestação Destinatário</a></li><li><a href="webServices.aspx?tipoConteudo=OUC/YVNWZfo=">Relação de Serviços Web</a></li><li><a href="consultaEPECConciliacao.aspx?tipoConteudo=dKnzIG+XQXM=">Consulta/Liberação de EPEC pendente de conciliação</a></li></ul></li><li class="itemMenuPrincipal"><a href="listaSubMenu.aspx?Id=ndIjl+iEFdE=">Legislação</a><ul class="dropdown"><li><a href="listaConteudo.aspx?tipoConteudo=3GhDwJ/ZeSI=">Ajustes SINIEF</a></li><li><a href="listaConteudo.aspx?tipoConteudo=8NGLm789Z+0=">Atos RFB/CGIBS</a></li><li><a href="listaConteudo.aspx?tipoConteudo=roKnnK+H7D0=">Atos Técnicos RFB/CGIBS</a></li><li><a href="listaConteudo.aspx?tipoConteudo=AX0vPC2u8xc=">Atos COTEPE</a></li><li><a href="listaConteudo.aspx?tipoConteudo=QIcipqxg0bU=">Convênios</a></li><li><a href="listaConteudo.aspx?tipoConteudo=gPWmdzYAb0Y=">Protocolos</a></li></ul></li><li class="itemMenuPrincipal"><a href="listaSubMenu.aspx?Id=04BIflQt1aY=">Documentos</a><ul class="dropdown"><li><a href="listaConteudo.aspx?tipoConteudo=ndIjl+iEFdE=">Manuais </a></li><li><a href="listaConteudo.aspx?tipoConteudo=BMPFMBoln3w=">Esquemas XML</a></li><li><a href="listaConteudo.aspx?tipoConteudo=04BIflQt1aY=">Notas Técnicas</a></li><li><a href="listaConteudo.aspx?tipoConteudo=hXzemuyNHW4=">Informes Técnicos</a></li><li><a href="listaConteudo.aspx?tipoConteudo=/NJarYc9nus=">Diversos</a></li></ul></li><li class="itemMenuPrincipal"><a href="listaSubMenu.aspx?Id=BMPFMBoln3w=">Downloads</a><ul class="dropdown"><li><a href="download.aspx?tipoConteudo=vBO/4eBj5F4=">Visualizador de DF-e</a></li><li><a href="download.aspx?tipoConteudo=OFrcUd5//Lg=">Assinador</a></li></ul></li><li class="itemMenuPrincipal"><a href="listaSubMenu.aspx?Id=VOYEgBgD3iU=">Outros DF-e</a><ul class="dropdown"><li><a href="?tipoConteudo=E1nOtSqZmEI=">NF3e</a><ul class="dropdown-submenu"><li><a href="?tipoConteudo=kIiniiSkpKc=">Esquemas XML</a></li><li><a href="listaConteudo.aspx?tipoConteudo=cKe3X6pJ+2Q=">Notas Técnicas</a></li></ul></li><li><a href="?tipoConteudo=VjrjMInPXGA=">NF-e ABI</a><ul class="dropdown-submenu"><li><a href="listaConteudo.aspx?tipoConteudo=bJi2vmx+jmw=">Manuais</a></li><li><a href="listaConteudo.aspx?tipoConteudo=v5k1Ww0z+Sw=">Diversos</a></li></ul></li><li><a href="listaConteudo.aspx?tipoConteudo=hwtReelpAJI=">NFAg</a><ul class="dropdown-submenu"><li><a href="listaConteudo.aspx?tipoConteudo=WfGRzCxQzW4=">Manuais</a></li><li><a href="listaConteudo.aspx?tipoConteudo=qvyq5vuft74=">Esquemas XML</a></li><li><a href="listaConteudo.aspx?tipoConteudo=U0LlsYVGBRU=">Diversos</a></li><li><a href="listaConteudo.aspx?tipoConteudo=pxmi2A8JQsI=">Notas Técnicas</a></li></ul></li><li><a href="listaConteudo.aspx?tipoConteudo=FM+KdU7EQrQ=">NFCom</a><ul class="dropdown-submenu"><li><a href="listaConteudo.aspx?tipoConteudo=OJQR7LXdlWA=">Esquemas XML</a></li><li><a href="listaConteudo.aspx?tipoConteudo=BDiib/SWUnA=">Notas Técnicas</a></li></ul></li><li><a href="listaConteudo.aspx?tipoConteudo=A/NFALwUh+4=">NFGas</a><ul class="dropdown-submenu"><li><a href="listaConteudo.aspx?tipoConteudo=S3kAYt9NTFw=">Manuais</a></li><li><a href="listaConteudo.aspx?tipoConteudo=rqiUX8LJYTU=">Esquemas XML</a></li><li><a href="listaConteudo.aspx?tipoConteudo=r1pBhiRUWSs=">Notas Técnicas</a></li></ul></li></ul></li></ul>
                    </div>
                </div>
                <div id="barraDireita">
                    <div id="estatisticas">
                        <h1>Estatísticas da NF-e</h1>
                        <span id="ctl00_lblTituloNfeAut">NF-e Autorizadas</span>
                        <br />
                        <div class="valorEstatistica">
                            <span id="ctl00_lblTotalNfeAut">364,853 milhões</span>
                        </div>
                        <span id="ctl00_lblTituloEmissores">Número de Emissores</span>
                        <br />
                        <div class="valorEstatistica">
                            <span id="ctl00_lblTotalEmissores">42,293 mil</span>
                        </div>
                        <a id="ctl00_hlkInfoEstatisticas" href="infoEstatisticas.aspx">... saiba mais</a>
                    </div>
                    <div id="busca">
                        <div id="ctl00_upnBuscar">
	
                                <input name="ctl00$txtPalavraChave" type="text" id="ctl00_txtPalavraChave" class="campoTextoBusca" />
                                
                                <input type="image" name="ctl00$ibtBuscar" id="ctl00_ibtBuscar" class="botaoBuscar" onmouseover="javascript: trocarImagem(this)" onmouseout="javascript: trocarImagem(this)" src="imagens/botao_buscar_Off_completo.png" />
                                
                            
</div>
                    </div>
                    <div id="linkAreaRestrita">
                        <p>
                            <a id="ctl00_hlkAreaRestrita" href="https://hom.nfe.fazenda.gov.br/arearestrita/inicial/autenticacao.aspx">Área Restrita do Fisco</a>
                        </p>
                    </div>
                    <div id="linkCentralNFe">
                        <p>
                            <a id="ctl00_hlkCentralAtendimento" href="https://www.serpro.gov.br/menu/suporte/central-de-atendimento-serpro-nfe-cte">Central de Atendimento</a>
                        </p>
                    </div>
                    <div id="linkFAQ">
                        <p>
                            <a id="ctl00_hlkFAQ" href="perguntasFrequentes.aspx?tipoConteudo=3Ow1nfTBzIo=">Perguntas Frequentes</a>
                        </p>
                    </div>
                    <div id="linkSefaz">
                        <p>
                            <span id="ctl00_lblPortaisSefaz">Portais e Secretarias</span>
                        </p>
                    </div>
                    <div id="linkBanners">
                        <p>
                            <span id="ctl00_lblPortaisEstaduais">Portais Estaduais da NF-e</span>
                            <br />
                            <?xml version="1.0" encoding="utf-8"?><select onchange="javascript: window.open(this.value)"><option value="">Selecione</option><option value="http://sefaznet.ac.gov.br/nfe/">Acre</option><option value="http://www.sefaz.al.gov.br/nfe/">Alagoas</option><option value="http://sistemas.sefaz.am.gov.br/nfeweb/portal/index.do">Amazonas</option><option value="http://www.sefaz.ba.gov.br/nfen/portal/home.htm">Bahia</option><option value="http://nfe.sefaz.ce.gov.br/">Ceará</option><option value="http://dec.fazenda.df.gov.br/">Distrito Federal</option><option value="http://internet.sefaz.es.gov.br/informacoes/nfe/">Espirito Santo</option><option value="https://www.economia.go.gov.br/receita-estadual/documentos-fiscais/nfe.html">Goiás</option><option value="https://sistemas1.sefaz.ma.gov.br/portalsefaz/jsp/pagina/pagina.jsf?codigo=11">Maranhão</option><option value="http://www.sefaz.mt.gov.br/portal/nfe/">Mato Grosso</option><option value="https://www.sefaz.ms.gov.br/documentos-fiscais-eletronicos/nf-e/">Mato Grosso do Sul</option><option value="http://www.sped.fazenda.mg.gov.br/">Minas Gerais</option><option value="http://www.sefa.pa.gov.br/site/">Pará</option><option value="https://www.sefaz.pb.gov.br/servirtual/documentos-fiscais/nf-e/consulta-completa">Paraíba</option><option value="http://www.sped.fazenda.pr.gov.br/">Paraná</option><option value="https://www.sefaz.pe.gov.br/Servicos/Nota-Fiscal-Eletronica/Paginas/Apresentacao.aspx">Pernambuco</option><option value="http://www.sefaz.pi.gov.br/conteudo_internet.php?p=nfe_home">Piauí</option><option value="http://www.fazenda.rj.gov.br/sefaz/faces/webcenter/faces/owResource.jspx?z=oracle.webcenter.doclib%21UCMServer%21UCMServer%2523dDocName%253A100998">Rio de Janeiro</option><option value="http://www.set.rn.gov.br/contentProducao/Aplicacao/SET_v2/nfe/gerados/inicio.asp">Rio Grande do Norte</option><option value="http://receita.fazenda.rs.gov.br/lista/2933/nf-e-(nota-fiscal-eletronica)">Rio Grande do Sul</option><option value="http://www2.sefin.ro.gov.br/manual/mostrar.asp?link=http://centralfacil.sefin.ro.gov.br/mostrar_manual.asp?id_conteudo=281">Rondônia</option><option value="https://www.sefaz.rr.gov.br/empresa/consultar-internamento-nf">Roraima</option><option value="http://nfe.sef.sc.gov.br/">Santa Catarina</option><option value="http://www.fazenda.sp.gov.br/nfe/">São Paulo</option><option value="http://nfe.sefaz.se.gov.br/">Sergipe</option><option value="http://www.sefaz.to.gov.br/">Tocantins</option></select>
                        </p>
                        <p>
                            <span id="ctl00_lblLinkSefaz">Secretarias de Fazenda</span>
                            <br />
                            <?xml version="1.0" encoding="utf-8"?><select onchange="javascript: window.open(this.value)"><option value="">Selecione</option><option value="http://www.sefaz.ac.gov.br/">Acre</option><option value="http://www.sefaz.al.gov.br/">Alagoas</option><option value="http://www.sefaz.ap.gov.br/">Amapá</option><option value="http://www.sefaz.am.gov.br/">Amazonas</option><option value="http://www.sefaz.ba.gov.br/">Bahia</option><option value="http://www.sefaz.ce.gov.br/">Ceará</option><option value="http://www.fazenda.df.gov.br/">Distrito Federal</option><option value="http://www.sefaz.es.gov.br/">Espirito Santo</option><option value="http://www.sefaz.go.gov.br/">Goiás</option><option value="http://www.sefaz.ma.gov.br/">Maranhão</option><option value="http://www.sefaz.mt.gov.br/">Mato Grosso</option><option value="http://www.sefaz.ms.gov.br/">Mato Grosso do Sul</option><option value="http://www.fazenda.mg.gov.br/">Minas Gerais</option><option value="http://www.sefa.pa.gov.br/">Pará</option><option value="https://www.sefaz.pb.gov.br/">Paraíba</option><option value="https://www.fazenda.pr.gov.br/">Paraná</option><option value="http://www.sefaz.pe.gov.br/">Pernambuco</option><option value="http://www.sefaz.pi.gov.br/">Piauí</option><option value="http://www.sefaz.rj.gov.br/">Rio de Janeiro</option><option value="http://www.set.rn.gov.br/">Rio Grande do Norte</option><option value="http://fazenda.rs.gov.br/inicial">Rio Grande do Sul</option><option value="http://www.sefin.ro.gov.br/">Rondônia</option><option value="http://www.sefaz.rr.gov.br/">Roraima</option><option value="http://www.sef.sc.gov.br/">Santa Catarina</option><option value="http://www.fazenda.sp.gov.br/">São Paulo</option><option value="http://www.sefaz.se.gov.br/">Sergipe</option><option value="http://www.sefaz.to.gov.br/">Tocantins</option></select>
                        </p>
                        
                        
                        <img id="linhaDivisoria" src="imagens/linha_divisoria.png" alt="Linha divisória" />
                        <div>
	<table cellspacing="0" rules="all" id="ctl00_gdvLinksDestaque" style="border-width:0px;border-collapse:collapse;">
		<tr>
			<td>
                                        <input type="image" name="ctl00$gdvLinksDestaque$ctl02$ImageButton1" id="ctl00_gdvLinksDestaque_ctl02_ImageButton1" onmouseover="javascript: trocarImagem(this)" onmouseout="javascript: trocarImagem(this)" title="Manifesto Eletrônico de Documentos Fiscais" src="imagens/banner_mdfe_Off.png" alt="Manifesto Eletrônico de Documentos Fiscais" onclick="aspnetForm.target =&#39;_blank&#39;;" />
                                    </td>
		</tr><tr>
			<td>
                                        <input type="image" name="ctl00$gdvLinksDestaque$ctl03$ImageButton1" id="ctl00_gdvLinksDestaque_ctl03_ImageButton1" onmouseover="javascript: trocarImagem(this)" onmouseout="javascript: trocarImagem(this)" title="Conhecimento de Transporte Eletrônico" src="imagens/banners_Visite_CTe_Off.png" alt="Conhecimento de Transporte Eletrônico" onclick="aspnetForm.target =&#39;_blank&#39;;" />
                                    </td>
		</tr><tr>
			<td>
                                        <input type="image" name="ctl00$gdvLinksDestaque$ctl04$ImageButton1" id="ctl00_gdvLinksDestaque_ctl04_ImageButton1" onmouseover="javascript: trocarImagem(this)" onmouseout="javascript: trocarImagem(this)" title="Sistema Público de Escrituração Fiscal" src="imagens/banners_Visite_Sped_Off.png" alt="Sistema Público de Escrituração Fiscal" onclick="aspnetForm.target =&#39;_blank&#39;;" />
                                    </td>
		</tr><tr>
			<td>
                                        <input type="image" name="ctl00$gdvLinksDestaque$ctl05$ImageButton1" id="ctl00_gdvLinksDestaque_ctl05_ImageButton1" onmouseover="javascript: trocarImagem(this)" onmouseout="javascript: trocarImagem(this)" title="Superintendência da Zona Franca de Manaus" src="imagens/banners_manaus_Off.png" alt="Superintendência da Zona Franca de Manaus" onclick="aspnetForm.target =&#39;_blank&#39;;" />
                                    </td>
		</tr><tr>
			<td>
                                        <input type="image" name="ctl00$gdvLinksDestaque$ctl06$ImageButton1" id="ctl00_gdvLinksDestaque_ctl06_ImageButton1" onmouseover="javascript: trocarImagem(this)" onmouseout="javascript: trocarImagem(this)" title="Portal Nacional do Bilhete de Passagem Eletrônico" src="imagens/banner_bpe_Off.png" alt="Portal Nacional do Bilhete de Passagem Eletrônico" onclick="aspnetForm.target =&#39;_blank&#39;;" />
                                    </td>
		</tr>
	</table>
</div>
                        
                    </div>
                </div>
                <div id="conteudo">
                    <div id="localizacao">
                        <div id="voceEstaAqui">
                            Você está aqui:
                        </div>
                        <div id="caminho">
                            <a id="ctl00_hlkPaginaPrincipao" href="principal.aspx">Página Principal</a>
                            <?xml version="1.0" encoding="utf-8"?>
    &gt;
    <a href="listaSubMenu.aspx?Id=BMPFMBoln3w=">Downloads</a>
      &gt;
      <span class="fonteCinza">Visualizador de DF-e</span>
                            
                            
                        </div>
                    </div>
                    <div id="zoomAcessibilidade">
                        <img src="imagens/acessibilidade_reduzir_Off.png" id="imgZoomMenos" onmouseover="javascript: trocarImagem(this)"
                            onmouseout="javascript: trocarImagem(this)" alt="Link que permite reduzir o tamanho da fonte" />
                        <img src="imagens/acessibilidade_ampliar_Off.png" id="imgZoomMais" onmouseover="javascript: trocarImagem(this)"
                            onmouseout="javascript: trocarImagem(this)" alt="Link que permite aumentar o tamanho da fonte" />
                    </div>
                    <div id="conteudoDinamico">
                        

    <?xml version="1.0" encoding="utf-8"?><div class="divTituloPrincipal" xmlns:dt="http://exslt.org/dates-and-times" xmlns:n="http://exslt.org/math"><label class="tituloPrincipal">Visualizador de DF-e</label></div><div class="indentacaoConteudo" xmlns:dt="http://exslt.org/dates-and-times" xmlns:n="http://exslt.org/math">O Visualizador é um aplicativo que permite visualizar documentos fiscais eletrônicos tais como Nota Fiscal Eletrônica(NF-e) e Conhecimento de Transporte Eletrônico(CT-e).<br /></div><div class="top25" xmlns:dt="http://exslt.org/dates-and-times" xmlns:n="http://exslt.org/math"><table class="tabelaListagemDados"><caption>Downloads para instalação manual</caption><th>Plataforma</th><th>Tamanho</th><th>Data</th><tr class="&#xD;&#xA;                        linhaImparCentralizada&#xD;&#xA;                      "><td class="colunaAlinhadaEsquerda"><img class="imagemSO" src="imagens/icone_Linux.png"></img><a target="blank" href="&#xD;&#xA;                            exibirArquivo.aspx?conteudo=655b+w/i/pw=">Linux GTK (Ubuntu) x86_64</a></td><td class="largura180">26.943 KB
                  </td><td class="largura180">06/08/2014</td></tr><tr class="&#xD;&#xA;                        linhaParCentralizada&#xD;&#xA;                      "><td class="colunaAlinhadaEsquerda"><img class="imagemSO" src="imagens/icone_windows.png"></img><a target="blank" href="&#xD;&#xA;                            exibirArquivo.aspx?conteudo=r/EyAgmzrxU=">Windows 64 bits</a></td><td class="largura180">26.947 KB
                  </td><td class="largura180">06/08/2014</td></tr><tr class="&#xD;&#xA;                        linhaImparCentralizada&#xD;&#xA;                      "><td class="colunaAlinhadaEsquerda"><img class="imagemSO" src="imagens/icone_Linux.png"></img><a target="blank" href="&#xD;&#xA;                            exibirArquivo.aspx?conteudo=4GruFyFXGVs=">Linux GTK (Ubuntu)</a></td><td class="largura180">32.677 KB
                  </td><td class="largura180">06/08/2014</td></tr><tr class="&#xD;&#xA;                        linhaParCentralizada&#xD;&#xA;                      "><td class="colunaAlinhadaEsquerda"><img class="imagemSO" src="imagens/icone_windows.png"></img><a target="blank" href="&#xD;&#xA;                            exibirArquivo.aspx?conteudo=BlzJUwsR70A=">Windows 32 bits</a></td><td class="largura180">26.958 KB
                  </td><td class="largura180">06/08/2014</td></tr></table></div><table class="tabelaFundoBege" xmlns:dt="http://exslt.org/dates-and-times" xmlns:n="http://exslt.org/math"><caption>Instalação via Java Web Start</caption><tr><td style="width: 25%"><a target="blank" href="visualizador/visualizador.jnlp">Instalação via Java Web Start</a></td><td><span style="font-weight: bold">ATENÇÃO: Caso essa versão de&nbsp;instalação não seja compatível como o Java instalado em seu computador, você deverá instalar uma versão mais atual do Java. Porém, qualquer versão anterior do Java será substituída pela versão mais nova. Se você possui algum software que necessite de uma versão específica do Java, consulte seu suporte técnico antes de atualizar.</span><br />
<br />
A tecnologia Java Web Start permite o download e a instalação automática do Visualizador eliminando procedimentos complexos de instalação ou atualização. <br />
Todas as inicializaçãoes seguintes deste aplicativo verificarão a existência de uma nova versão disponível, que poderá ser instalada de acordo com o interesse do usuário.<br /></td></tr></table><table class="tabelaFundoBege" xmlns:dt="http://exslt.org/dates-and-times" xmlns:n="http://exslt.org/math"><caption>Pré-Requisitos de Instalação</caption><tr><td style="width: 25%"><a target="blank" href="http://www.java.com/pt_BR/download/manual.jsp">Máquina Virtual Java (JVM)</a></td><td>              É necessário ter a Máquina Virtual Java(JVM) instalada no computador para que o aplicativo funcione.</td></tr></table><table class="tabelaFundoBege" xmlns:dt="http://exslt.org/dates-and-times" xmlns:n="http://exslt.org/math"><caption>Perguntas Frequentes</caption><tr><td style="width: 25%"><a target="blank" href="&#xD;&#xA;                          exibirArquivo.aspx?conteudo=Z1ivX0aahCM=">Perguntas Frequentes (FAQ)</a></td><td>Este documento apresenta as respostas para as dúvidas mais frequentes sobre instalação e uso do Visualizador de DF-e.</td></tr></table>

                    </div>
                </div>
            </div>
            <div id="rodape">
                <div id="sombraRodape">
                </div>
                <div id="conteudoRodape">
                    <div id="menuRodape">
                        <?xml version="1.0" encoding="utf-8"?><a href="listaSubMenu.aspx?Id=6H4uVlIEaKs=">Conheça a NF-e</a><a href="listaSubMenu.aspx?Id=esCrSQFUvGg=">Serviços</a><a href="listaSubMenu.aspx?Id=ndIjl+iEFdE=">Legislação</a><a href="listaSubMenu.aspx?Id=04BIflQt1aY=">Documentos</a><a href="listaSubMenu.aspx?Id=BMPFMBoln3w=">Downloads</a><a href="https://hom.nfe.fazenda.gov.br/arearestrita/inicial/autenticacao.aspx">Área Restrita</a><a href="https://hom.nfe.fazenda.gov.br/arearestrita/inicial/listaSubMenu.aspx?Id=UORZ3ynALMA=">Documentos e outros</a><a href="listaSubMenu.aspx?Id=VOYEgBgD3iU=">Outros DF-e</a>
                        <span id="ctl00_lblPortalRodape" class="labelPortalRodape">Portal da NF-e 2026 - Nota Fiscal Eletrônica  v2.9.9.0</span>
                    </div>
                    <div id="marcaReceita">
                        <a href="//www.receita.fazenda.gov.br" target="_blank" class="imgReceita">
                            <!--img src="imagens/marca_Receita.png" class="imgReceita" alt="Link para o sítio da Receita Federal"/-->
                            Receita Federal </a>
                    </div>
                </div>
            </div>

            <div id="tipoAmbiente">
                <span id="ctl00_lblAmbiente">Ambiente de Homologação</span>
            </div>

        

<script type="text/javascript">
//<![CDATA[
Sys.Application.add_init(function() {
    $create(AjaxControlToolkit.AutoCompleteBehavior, {"completionListCssClass":"popupBusca","delimiterCharacters":"(),.! ","id":"ctl00_aceAutoCompletarBusca","minimumPrefixLength":1,"serviceMethod":"ListarAutocompletarCampoPesquisar","servicePath":"AutoCompletarBusca.asmx"}, null, null, $get("ctl00_txtPalavraChave"));
});
//]]>
</script>
</form>
    </div>
</body>

</html>
