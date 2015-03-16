<table class="groupTable">
    <tr>
        <td colspan="2">
            <div class="groupTitle">${ _("HTTP API details") }</div>
        </td>
    </tr>
    <tr>
        <td class="dataCaptionTD"><span class="dataCaptionFormat">${ _("API Key")}</span></td>
        <td class="blacktext">
            ${apiKey.token if apiKey else _('None')}
            % if apiKey and apiKey.is_blocked:
                <span class="warningText">Blocked ${inlineContextHelp(_('Your API key has been blocked. Please contact an administrator for details.'))}</span>
            % endif
        </td>
    </tr>
    % if signingEnabled:
        <tr>
            <td class="dataCaptionTD"><span class="dataCaptionFormat">${ _("Secret Key")}</span></td>
            <td class="blacktext">
                ${apiKey.secret if apiKey else _('None')}
            </td>
        </tr>
    % endif
    <tr>
        <td nowrap class="dataCaptionTD"><span class="dataCaptionFormat">${ _("Created")}</span></td>
        <td class="blacktext">
            ${formatDateTime(apiKey.created_dt) if apiKey else _('n/a')}
        </td>
    </tr>
    <tr>
        <td nowrap class="dataCaptionTD"><span class="dataCaptionFormat">${ _("Last used")}</span></td>
        <td class="blacktext">
            ${apiKey.last_used_dt and formatDateTime(apiKey.last_used_dt) or _('Never') if apiKey else _('n/a')}
        </td>
    </tr>
    <tr>
        <td nowrap class="dataCaptionTD"><span class="dataCaptionFormat">${ _("Last used by")}</span></td>
        <td class="blacktext">
            ${apiKey.last_used_ip or _('n/a') if apiKey else _('n/a')}
        </td>
    </tr>
    <tr>
        <td nowrap class="dataCaptionTD"><span class="dataCaptionFormat">${ _("Last request")}</span></td>
        <td class="blacktext">
            % if apiKey and apiKey.last_used_uri:
                ${escape(apiKey.last_used_uri)} (${_('Authenticated') if apiKey.last_used_auth else 'Public'})
            % else:
                ${_('n/a')}
            % endif
        </td>
    </tr>
    <tr>
        <td nowrap class="dataCaptionTD"><span class="dataCaptionFormat">${ _("Total uses")}</span></td>
        <td class="blacktext">
            ${apiKey.use_count if apiKey else _('n/a')}
        </td>
    </tr>
    % if not apiKey or not apiKey.is_blocked:
        <tr>
            <td></td>
            <td>
                % if not apiKey:
                    <form action="${urlHandlers.UHUserAPICreate.getURL(avatar)}" method="POST" style="display: inline;">
                        <input type="submit" id="createAPIKey" value="${_('Create API key')}">
                    </form>
                % else:
                    <form action="${urlHandlers.UHUserAPICreate.getURL(avatar)}" method="POST" style="display: inline;">
                        <input type="submit" id="createNewAPIKey" value="${_('Create a new API key pair')}">
                    </form>
                    % if persistentAllowed:
                         <input type="submit" id="enablePersistentSignatures" data-enabled="${'1' if apiKey.is_persistent_allowed else '0'}" value="${(_('Disable') if apiKey.is_persistent_allowed else _('Enable')) + _(' persistent signatures')}" />
                         <div style="display:inline;" id="progressPersistentSignatures"></div>
                    % endif
                % endif
            </td>
        </tr>
    % endif

    % if isAdmin:
        <tr>
            <td colspan="2">
                <div class="groupTitle">${ _("Administration") }</div>
            </td>
        </tr>
        % if apiKey:
            <tr>
                <td></td>
                <td>
                    <form action="${urlHandlers.UHUserAPIBlock.getURL(avatar)}" method="POST" style="display:inline;">
                        <input type="submit" value="${_('Unblock API key') if apiKey.is_blocked else _('Block API key')}">
                    </form>

                    <form action="${urlHandlers.UHUserAPIDelete.getURL(avatar)}" method="POST" style="display:inline;">
                        <input type="submit" id="deleteAPIKey" value="${_('Delete API key')}" />
                    </form>
                </td>
            </tr>
            <tr>
                 <td nowrap class="dataCaptionTD"><span class="dataCaptionFormat">${ _("Old keys") }</span></td>
                 <td class="blacktext">
                    % if old_keys:
                        <ul>
                            % for key in old_keys:
                                <li>${key.token} (${_('used {} times').format(key.use_count)})</li>
                            % endfor
                        </ul>
                    % else:
                        None
                    % endif
                 </td>
             </tr>
        % else:
            <tr>
                <td colspan="2" class="blacktext">
                    ${_('No actions available')}
                </td>
            </tr>
        % endif
    % endif
</table>

<script type="text/javascript">
    var disableText = ${ apiPersistentDisableAgreement | n,j };
    var enableText = ${ apiPersistentEnableAgreement | n,j };

    $('#enablePersistentSignatures').click(function(e) {
        var confirmHandler= function(value){
            if(value){
                $E('progressPersistentSignatures').set(progressIndicator(true, false));
                indicoRequest('user.togglePersistentSignatures', {userId: '${avatar.getId()}'},
                    function(result, error) {
                        $E('progressPersistentSignatures').set('');
                        if (error){
                            IndicoUI.Dialogs.Util.error(error);
                        }
                        else{
                            $('#enablePersistentSignatures').val((result ? $T('Disable') : $T('Enable')) + $T(' persistent signatures'));
                            $('#enablePersistentSignatures').data("enabled", result == true ? "1" : "0");
                        }
                    });
            }
        };
        new ConfirmPopup($T("Persistent signatures"), Html.div({style: {width: '350px'}},$(this).data("enabled") == "1" ? disableText : enableText), confirmHandler).open();
    });
% if not apiKey or not apiKey.is_blocked:
    % if not apiKey:
    $("#createAPIKey").click(function(){
        var self = this;
        new ConfirmPopup($T("Create API Key"),$T("Please only create an API key if you actually need one. Unused API keys might be deleted after some time."), function(confirmed) {
            if(confirmed) {
                $(self).closest("form").submit();
            }
        }).open();
        return false;
    });
    % else:
    $("#createNewAPIKey").click(function(){
        var self = this;
        new ConfirmPopup($T("Create a new API Key pair"),$T("'Warning: When creating a new API key pair, your old key pair will stop working immediately!"), function(confirmed) {
            if(confirmed) {
                $(self).closest("form").submit();
            }
        }).open();
        return false;
    });
    % endif
% endif
% if apiKey and isAdmin:
    $("#deleteAPIKey").click(function(){
        var self = this;
        new ConfirmPopup($T("Delete API Key"),$T("Do you really want to delete the API key? The user will be able to create a new key."), function(confirmed) {
            if(confirmed) {
                $(self).closest("form").submit();
            }
        }).open();
        return false;
    });
% endif
</script>
