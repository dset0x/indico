<%
if bgColorCode:
    bgColorStyle = """ style="background: #%s; border-color: #%s;" """%(bgColorCode, bgColorCode)
else:
    bgColorStyle = ""

if textColorCode:
    textColorStyle = """ style="color: #%s;" """%(textColorCode)
else:
    textColorStyle = ""
%>


<div class="conf clearfix" itemscope itemtype="http://schema.org/Event">
    <div class="confheader clearfix" ${ bgColorStyle }>
        <div class="confTitleBox" ${ bgColorStyle }>
            <div class="confTitle">
                <h1>
                    <a href="${ displayURL }">
                        <span class="conferencetitlelink" ${textColorStyle}>
                            % if logo :
                                <div class="confLogoBox">
                                   ${ logo }
                                </div>
                            % endif
                            <span itemprop="title">${ confTitle }</span>
                        </span>
      </a>
                </h1>
           </div>
        </div>
        <div class="confSubTitleBox" ${ bgColorStyle }>
            <div class="confSubTitleContent">
                ${ template_hook('conference-header', event=conf) }
                <div class="confSubTitle" ${ textColorStyle }>
                   <div class="datePlace">
                        <div class="date">${ confDateInterval }</div>
                        <div class="place">${ confLocation }</div>
                        <div class="timezone">${ timezone } timezone</div>
                    </div>
                    % if nowHappening:
                        <div class="nowHappening" ${ textColorStyle }>${ nowHappening }</div>
                    % endif
                    ${ template_hook('conference-header-subtitle', event=conf) }
                </div>
            </div>
        </div>
        % if simpleTextAnnouncement:
            <div class="simpleTextAnnouncement">${ simpleTextAnnouncement }</div>
        % endif
    </div>
    <div id="confSectionsBox" class="clearfix">
    ${ render_template('flashed_messages.html') }
    ${ menu }
    ${ body }
    </div>
    <script>
        $(document).ready(function() {
            $('h1, .subLevelTitle, .subEventLevelTitle, .topLevelTitle').mathJax();
        });
    </script>
</div>
